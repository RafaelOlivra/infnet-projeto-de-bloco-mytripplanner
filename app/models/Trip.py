import json
import csv
import base64
from io import StringIO

from services.TripData import TripData
from services.LatLong import LatLong
from services.OpenWeatherMap import OpenWeatherMap
from services.Utils import Utils

from models.TripModel import TripModel


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

        # Get weather forecast for the trip
        trip_data["weather"] = OpenWeatherMap().get_forecast_for_next_5_days(
            trip_data.get("destination_city"), trip_data.get("destination_state")
        )

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
        data["weather_base64"] = base64.b64encode(
            json.dumps(data.pop("weather")).encode()
        ).decode()
        data["tags"] = ", ".join(data["tags"])

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace("\n", " ")

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

            weather_data = base64.b64decode(data.pop("weather_base64")).decode()
            data["weather"] = json.loads(weather_data)
            data["tags"] = [tag.strip() for tag in data["tags"].split(",")]

            # Remove the id field if it exists so a new ID is generated
            data.pop("id", None)

            return cls(trip_data=data)
        except Exception as e:
            raise ValueError(
                "The CSV data is not in the correct format. Please check the data and try again."
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
