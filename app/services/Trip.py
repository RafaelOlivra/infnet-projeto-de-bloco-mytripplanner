import json
import csv
import base64

from datetime import datetime, date
from io import StringIO
from datetime import datetime

from lib.LatLong import LatLong
from lib.Utils import Utils

from services.TripData import TripData
from services.OpenWeatherMap import OpenWeatherMap

from models.Weather import ForecastModel


class Trip:
    def __init__(self, id: str = None, trip_data: dict = None):
        if id:
            self.id = id
            if not self._load():
                raise ValueError(f"Trip with ID {self.id} could not be loaded.")
        elif trip_data:
            self.create(trip_data)

    # --------------------------
    # CRUD Operations
    # --------------------------
    def create(self, trip_data: dict):
        if not trip_data:
            raise ValueError("Trip data is required to create a trip.")

        trip_data["slug"] = Utils().slugify(trip_data.get("title", ""))

        # Get coordinates for origin and destination
        origin_coords = self._get_or_fetch_coordinates(
            trip_data,
            "origin_longitude",
            "origin_latitude",
            trip_data.get("origin_city"),
            trip_data.get("origin_state"),
        )
        trip_data["origin_longitude"], trip_data["origin_latitude"] = origin_coords

        dest_coords = self._get_or_fetch_coordinates(
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

        # Get weather forecast for the trip if not provided
        if "weather" not in trip_data:
            trip_data["weather"] = OpenWeatherMap().get_forecast_for_next_5_days(
                trip_data.get("destination_city"), trip_data.get("destination_state")
            )

        # Store weather that are within the trip dates
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
        self.id = self.model.id
        self.slug = self.model.slug
        return self._save()

    def update(self, trip_data: dict):
        updated_data = self.model.dict()
        updated_data.update(trip_data)

        # Get coordinates for origin and destination if they have changed
        if (
            trip_data.get("origin_city") != self.model.origin_city
            or trip_data.get("origin_state") != self.model.origin_state
        ):
            updated_data["origin_longitude"], updated_data["origin_latitude"] = (
                self._get_coordinates(
                    trip_data.get("origin_city", self.model.origin_city),
                    trip_data.get("origin_state", self.model.origin_state),
                )
            )

        if (
            trip_data.get("destination_city") != self.model.destination_city
            or trip_data.get("destination_state") != self.model.destination_state
        ):
            (
                updated_data["destination_longitude"],
                updated_data["destination_latitude"],
            ) = self._get_coordinates(
                trip_data.get("destination_city", self.model.destination_city),
                trip_data.get("destination_state", self.model.destination_state),
            )

        self.model = TripModel(**updated_data)
        self._save()
        return self

    def delete(self):
        return TripData().delete(self.model.id)

    # --------------------------
    # Export/Import
    # --------------------------
    def to_json(self):
        return self.model.json()

    def to_csv(self):
        data = self.model.dict()

        # Convert dates to strings
        data["start_date"] = Utils.format_date_str(data["start_date"])
        data["end_date"] = Utils.format_date_str(data["end_date"])

        data["weather_base64"] = base64.b64encode(
            json.dumps(data.pop("weather")).encode()
        ).decode()

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

    @classmethod
    def from_json(cls, json_string) -> "Trip":
        try:
            data = json.loads(json_string)

            # Remove the id field if it exists so a new ID is generated
            data.pop("id", None)

            return cls(trip_data=data)
        except Exception as e:
            raise ValueError(
                "The JSON data is not in the correct format. Please check the data and try again."
            )

    @classmethod
    def from_csv(cls, csv_data) -> "Trip":
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

            return cls(trip_data=data)
        except Exception as e:
            raise ValueError(
                f"The CSV data is not in the correct format. Please check the data and try again. {e}"
            )

    # --------------------------
    # Data Operations
    # --------------------------

    def _load(self):
        trip = TripData().get(self.id)
        if not trip:
            return False
        self.model = trip
        self.id = trip.id
        self.slug = trip.slug
        return True

    def _save(self):
        return TripData().save(value=self.model, id=self.model.id)

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

    def _get_or_fetch_coordinates(self, trip_data, lon_key, lat_key, city, state):
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
