import json
import csv
import base64

from datetime import datetime, timedelta
from io import StringIO
from datetime import datetime

from lib.LatLong import LatLong
from lib.Utils import Utils

from services.TripData import TripData
from services.OpenWeatherMap import OpenWeatherMap

from models.Weather import ForecastModel
from models.Trip import TripModel


class Trip:
    def __init__(self, trip_id: str = None, trip_data: dict = None, date_verify=True):
        if trip_id:
            if not self._load(trip_id):
                raise ValueError(f"Trip with ID {trip_id} could not be loaded.")
        elif trip_data:
            self.create(trip_data, date_verify=date_verify)

    # --------------------------
    # CRUD Operations
    # --------------------------
    def create(self, trip_data: dict, date_verify=True) -> bool:
        if not trip_data:
            raise ValueError("Trip data is required to create a trip.")

        # Unset some fields that should not be set by the user
        trip_data.pop("id", None)
        trip_data.pop("created_at", None)

        trip_data["slug"] = Utils().slugify(trip_data.get("title", ""))

        # Get coordinates for origin and destination
        origin_coords = self._get_or_load_coordinates(
            trip_data,
            "origin_longitude",
            "origin_latitude",
            trip_data.get("origin_city"),
            trip_data.get("origin_state"),
        )
        trip_data["origin_longitude"], trip_data["origin_latitude"] = origin_coords

        dest_coords = self._get_or_load_coordinates(
            trip_data,
            "destination_longitude",
            "destination_latitude",
            trip_data.get("destination_city"),
            trip_data.get("destination_state"),
        )
        trip_data["destination_longitude"], trip_data["destination_latitude"] = (
            dest_coords
        )

        # Convert the date strings to datetime objects if not already
        trip_data["start_date"] = Utils.to_datetime(trip_data["start_date"])
        trip_data["end_date"] = Utils.to_datetime(trip_data["end_date"])

        # Make sure the start date is not in the past
        if date_verify and trip_data["start_date"] < (
            datetime.now() - timedelta(days=1)
        ):
            raise ValueError("The start date must be in the future.")

        # Make sure start date is before end date
        if trip_data["start_date"] > trip_data["end_date"]:
            raise ValueError("The start date must be before the end date.")

        # Get weather forecast for the trip if not provided
        if "weather" not in trip_data:
            trip_data["weather"] = OpenWeatherMap().get_forecast_for_next_5_days(
                trip_data.get("destination_city"), trip_data.get("destination_state")
            )

        # Only store weather that are within the trip dates
        if "weather" in trip_data:
            weather = []
            for forecast in trip_data["weather"]:
                # Convert to ForecastModel object if not already
                if type(forecast) != ForecastModel:
                    forecast = ForecastModel(**forecast)

                # Convert the date string to a datetime object
                if isinstance(forecast.date, str):
                    forecast.date = Utils.to_datetime(forecast.date)

                # Check if the forecast date is within the trip dates
                if (
                    trip_data.get("start_date")
                    <= forecast.date
                    <= trip_data.get("end_date")
                ):
                    # Convert the date back to a string
                    forecast.date = str(forecast.date)
                    weather.append(forecast)
            trip_data["weather"] = weather

        self.model = TripModel(**trip_data)
        return self._save()

    def get(self, attribute: str = None):
        if not self.model:
            return None
        return self.model.__getattribute__(attribute)

    # Implement the __getitem__ method to allow getting attributes using the [] notation
    def __getitem__(self, attribute: str = None):
        return self.get(attribute)

    def update(self, trip_data: dict) -> bool:
        updated_data = self.model.model_dump()
        updated_data.update(trip_data)

        # Get coordinates for origin and destination if they have changed
        if trip_data.get("origin_city") != self.get("origin_city") or trip_data.get(
            "origin_state"
        ) != self.get("origin_state"):
            updated_data["origin_longitude"], updated_data["origin_latitude"] = (
                self._get_coordinates(
                    trip_data.get("origin_city", self.get("origin_city")),
                    trip_data.get("origin_state", self.get("origin_state")),
                )
            )

        if trip_data.get("destination_city") != self.get(
            "destination_city"
        ) or trip_data.get("destination_state") != self.get("destination_state"):
            (
                updated_data["destination_longitude"],
                updated_data["destination_latitude"],
            ) = self._get_coordinates(
                trip_data.get("destination_city", self.get("destination_city")),
                trip_data.get("destination_state", self.get("destination_state")),
            )

        self.model = TripModel(**updated_data)
        return self._save()

    def delete(self) -> bool:
        if not self.model:
            return False
        if TripData().delete(self.get("id")):
            self.model = None
            return True

    # --------------------------
    # Export/Import
    # --------------------------
    def to_json(self):
        return self.model.model_dump_json()

    def to_csv(self):
        data = self.model.model_dump(serialize_as_any=True)

        # Convert dates to strings
        data["start_date"] = Utils.to_date_string(data["start_date"])
        data["end_date"] = Utils.to_date_string(data["end_date"])
        data["created_at"] = Utils.to_date_string(data["created_at"])

        # Serialize datetime objects
        if "weather" in data:
            for forecast in data["weather"]:
                forecast["date"] = Utils.to_date_string(forecast["date"])

        data["weather_base64"] = base64.b64encode(
            json.dumps(data.pop("weather")).encode()
        ).decode()

        # Convert attractions fields to strings
        if "attractions" in data:
            for attraction in data["attractions"]:
                if "url" in attraction:
                    attraction["url"] = str(attraction["url"])
                if "image" in attraction:
                    attraction["image"] = str(attraction["image"])
                if "created_at" in attraction:
                    attraction["created_at"] = Utils.to_date_string(
                        attraction["created_at"]
                    )

        data["attractions_base64"] = base64.b64encode(
            json.dumps(data.pop("attractions")).encode()
        ).decode()

        # Convert tags to a string
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = ",".join(data["tags"])

        # Replace reserved characters with placeholders
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace("\n", "____NEW_LINE____").replace(
                    ",", "____COMMA____"
                )

        csv_data = StringIO()
        writer = csv.DictWriter(csv_data, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

        return csv_data.getvalue()

    def from_json(self, json_string) -> "Trip":
        try:
            data = json.loads(json_string)

            # Remove the id field if it exists so a new ID is generated
            data.pop("id", None)

            return Trip(trip_data=data, date_verify=False)
        except Exception as e:
            raise ValueError(
                "The JSON data is not in the correct format. Please check the data and try again."
            )

    def from_csv(self, csv_data) -> "Trip":
        try:
            reader = csv.DictReader(StringIO(csv_data))
            data = next(reader)

            if "weather_base64" in data:
                weather_data = base64.b64decode(data.pop("weather_base64")).decode()
                data["weather"] = json.loads(weather_data)

            if "attractions_base64" in data:
                attractions_data = base64.b64decode(
                    data.pop("attractions_base64")
                ).decode()
                data["attractions"] = json.loads(attractions_data)

            # Replace the placeholder with commas and new lines
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.replace("____NEW_LINE____", "\n").replace(
                        "____COMMA____", ","
                    )

            # If tags is a string, convert it to a list
            if "tags" in data and data["tags"] and isinstance(data["tags"], str):
                data["tags"] = data["tags"].strip()
                data["tags"] = [tag.strip() for tag in data["tags"].split(",")]
            else:
                data["tags"] = []

            # Remove the id field if it exists so a new ID is generated
            data.pop("id", None)

            return Trip(trip_data=data, date_verify=False)
        except Exception as e:
            raise ValueError(
                f"The CSV data is not in the correct format. Please check the data and try again. {e}"
            )

    def from_model(self, trip_model: TripModel) -> "Trip":
        self.model = trip_model
        return self

    # --------------------------
    # Data Operations
    # --------------------------

    def _load(self, trip_id: str) -> bool:
        trip = TripData().get(trip_id)
        if not trip:
            return False
        self.model = trip
        return True

    def _save(self) -> bool:
        if not TripData().save(trip_data=self.model, trip_id=self.get("id")):
            self.model = None
            return False

    # --------------------------
    # Utils
    # --------------------------

    @staticmethod
    def _calculate_trip_length(start_date: datetime = None, end_date: datetime = None):
        if not start_date or not end_date:
            return 0

        try:
            return (end_date - start_date).days + 1
        except Exception as e:
            return 0

    @staticmethod
    def _get_coordinates(city, state):
        return LatLong().get_coordinates(city, state)

    def _get_or_load_coordinates(self, trip_data, lon_key, lat_key, city, state):
        if lon_key in trip_data and lat_key in trip_data:
            return trip_data[lon_key], trip_data[lat_key]
        return self._get_coordinates(city, state)

    @staticmethod
    def _get_travel_by_options():
        return {
            "driving": "🚗 Carro",
            "walking": "🚶 A pé",
            "bicycling": "🚴 Bicicleta",
            "transit": "🚇 Transporte Público",
            "flying": "✈️ Avião",
        }

    @staticmethod
    def get_travel_by_icon(travel_by) -> str:
        icon = Trip._get_travel_by_options().get(travel_by, "🚗 Carro")
        return icon.split(" ")[0]
