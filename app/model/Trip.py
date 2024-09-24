import uuid
from datetime import datetime
from services.TripData import TripData
from services.LatLong import LatLong
from services.OpenWeatherMap import OpenWeatherMap
from services.Utils import Utils
import json
import csv
import base64
from io import StringIO


class Trip:
    id: str
    slug: str
    title: str
    origin_city: str
    origin_state: str
    origin_longitude: float
    origin_latitude: float
    destination_city: str
    destination_state: str
    destination_longitude: float
    destination_latitude: float
    start_date: datetime
    end_date: datetime
    weather: dict
    goals: str
    activities: list
    notes: str
    tags: list

    def __init__(self, id: str = None, trip_data: dict = None):
        if id:
            self.id = id
            if not self._load():
                raise ValueError(
                    f"Trip with ID {self.id} could not be loaded.")
        elif trip_data:
            self.create(trip_data)

    # --------------------------
    # Main Methods
    # --------------------------

    def create(self, trip_data: dict):
        if not trip_data:
            raise ValueError("Trip data is required to create a trip.")

        self.id = self._generate_id()
        self.title = trip_data.get("title", "")
        self.slug = Utils().slugify(self.title)
        self.origin_city = trip_data.get("origin_city", "")
        self.origin_state = trip_data.get("origin_state", "")
        self.destination_city = trip_data.get("destination_city", "")
        self.destination_state = trip_data.get("destination_state", "")
        self.start_date = trip_data.get(
            "start_date", datetime.now().strftime(self._get_time_format()))
        self.end_date = trip_data.get(
            "end_date", datetime.now().strftime(self._get_time_format()))
        self.weather = trip_data.get("weather", {})
        self.goals = trip_data.get("goals", "")
        self.activities = trip_data.get("activities", [])
        self.notes = trip_data.get("notes", "")
        self.tags = trip_data.get("tags", [])

        self.origin_longitude, self.origin_latitude = self._get_or_fetch_coordinates(
            trip_data, "origin_longitude", "origin_latitude", self.origin_city, self.origin_state)
        self.destination_longitude, self.destination_latitude = self._get_or_fetch_coordinates(
            trip_data, "destination_longitude", "destination_latitude", self.destination_city, self.destination_state)

        self.weather = OpenWeatherMap().get_forecast_for_next_5_days(
            self.destination_city, self.destination_state)

        return self._save()

    def update(self, trip_data: dict):
        self.title = trip_data.get("title", self.title)
        self.slug = trip_data.get("slug", self.slug)
        self.origin_city = trip_data.get("origin_city", self.origin_city)
        self.origin_state = trip_data.get("origin_state", self.origin_state)
        self.destination_city = trip_data.get(
            "destination_city", self.destination_city)
        self.destination_state = trip_data.get(
            "destination_state", self.destination_state)
        self.start_date = trip_data.get("start_date", self.start_date)
        self.end_date = trip_data.get("end_date", self.end_date)
        self.weather = trip_data.get("weather", self.weather)
        self.goals = trip_data.get("goals", self.goals)
        self.activities = trip_data.get("activities", self.activities)
        self.notes = trip_data.get("notes", self.notes)
        self.tags = trip_data.get("tags", self.tags)

        if trip_data.get("origin_city", self.origin_city) != self.origin_city or \
                trip_data.get("origin_state", self.origin_state) != self.origin_state:
            self._update_coordinates("origin")

        if trip_data.get("destination_city", self.destination_city) != self.destination_city or \
                trip_data.get("destination_state", self.destination_state) != self.destination_state:
            self._update_coordinates("destination")

        return self

    def delete(self):
        return TripData().delete(self.id)

    # --------------------------
    # Import and Export
    # --------------------------

    def to_json(self):
        return json.dumps(self._get_trip_data_object())

    def to_csv(self):
        data = json.loads(self.to_json())
        data["weather_base64"] = base64.b64encode(
            json.dumps(data.pop("weather")).encode()).decode()
        data["tags"] = ", ".join(data["tags"])

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace("\n", " ")

        csv_data = StringIO()
        writer = csv.DictWriter(csv_data, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

        return csv_data.getvalue()

    def from_json(self, json_string):
        try:
            data = json.loads(json_string)
            data["trip_id"] = self._generate_id()

            return Trip(trip_data=data)
        except Exception as e:
            raise ValueError(
                "The JSON data is not in the correct format. Please check the data and try again.")

    def from_csv(self, csv_data):
        try:
            reader = csv.DictReader(StringIO(csv_data))
            data = next(reader)

            weather_data = base64.b64decode(
                data.pop("weather_base64")).decode()
            data["weather"] = json.loads(weather_data)
            data["tags"] = [tag.strip() for tag in data["tags"].split(",")]
            data["trip_id"] = self._generate_id()
            return Trip(trip_data=data)
        except Exception as e:
            raise ValueError(
                "The CSV data is not in the correct format. Please check the data and try again.")

    # --------------------------
    # Data Handling
    # --------------------------

    def _load(self):
        trip_data = TripData().get_trip_data(self.id)
        if not trip_data or not self._validate(trip_data):
            return False

        trip_data = self._sanitize(trip_data)
        self._assign_trip_data(trip_data)
        return True

    def _save(self):
        return TripData().save(value=self.to_json(), id=self.id)

    def _get_trip_data_object(self):
        return {
            "trip_id": self.id,
            "title": self.title,
            "slug": self.slug,
            "origin_city": self.origin_city,
            "origin_state": self.origin_state,
            "origin_longitude": self.origin_longitude,
            "origin_latitude": self.origin_latitude,
            "destination_city": self.destination_city,
            "destination_state": self.destination_state,
            "destination_longitude": self.destination_longitude,
            "destination_latitude": self.destination_latitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "weather": self.weather,
            "goals": self.goals,
            "activities": self.activities,
            "notes": self.notes,
            "tags": self.tags
        }

    def _assign_trip_data(self, trip_data):
        self.title = trip_data["title"]
        self.slug = trip_data.get("slug", Utils().slugify(self.title))
        self.origin_city = trip_data["origin_city"]
        self.origin_state = trip_data["origin_state"]
        self.destination_city = trip_data["destination_city"]
        self.destination_state = trip_data["destination_state"]
        self.start_date = trip_data["start_date"]
        self.end_date = trip_data["end_date"]
        self.weather = trip_data.get("weather", {})
        self.goals = trip_data.get("goals", "")
        self.activities = trip_data.get("activities", [])
        self.notes = trip_data.get("notes", "")
        self.tags = trip_data.get("tags", [])
        self.origin_longitude = trip_data.get("origin_longitude")
        self.origin_latitude = trip_data.get("origin_latitude")
        self.destination_longitude = trip_data.get("destination_longitude")
        self.destination_latitude = trip_data.get("destination_latitude")

    def _update_coordinates(self, location_type):
        if location_type == "origin":
            self.origin_longitude, self.origin_latitude = self._get_coordinates(
                self.origin_city, self.origin_state)
        elif location_type == "destination":
            self.destination_longitude, self.destination_latitude = self._get_coordinates(
                self.destination_city, self.destination_state)

        self._save()

    # --------------------------
    # Data Validation and Sanitization
    # --------------------------

    def _validate(self, trip_data):
        required_fields = ["title", "origin_city", "origin_state",
                           "destination_city", "destination_state", "start_date", "end_date"]
        for field in required_fields:
            if not trip_data.get(field):
                return False

        try:
            datetime.strptime(trip_data["start_date"], self._get_time_format())
            datetime.strptime(trip_data["end_date"], self._get_time_format())
        except ValueError:
            return False

        return True

    def _sanitize(self, trip_data):
        trip_data["title"] = trip_data["title"].strip()
        trip_data["start_date"] = datetime.strptime(
            trip_data["start_date"], self._get_time_format()).strftime(self._get_time_format())
        trip_data["end_date"] = datetime.strptime(
            trip_data["end_date"], self._get_time_format()).strftime(self._get_time_format())
        trip_data["weather"] = trip_data.get("weather", {})
        trip_data["activities"] = trip_data.get("activities", [])
        trip_data["tags"] = trip_data.get("tags", [])
        trip_data["goals"] = trip_data["goals"].strip()
        trip_data["notes"] = trip_data["notes"].strip()

        return trip_data

    # --------------------------
    # Utils
    # --------------------------

    def _generate_id(self):
        return str(uuid.uuid4())

    def _get_time_format(self):
        return "%Y-%m-%d %H:%M"

    def _get_coordinates(self, city, state):
        return LatLong().get_coordinates(city, state)

    def _get_or_fetch_coordinates(self, trip_data, lon_key, lat_key, city, state):
        if lon_key in trip_data and lat_key in trip_data:
            return trip_data[lon_key], trip_data[lat_key]
        return self._get_coordinates(city, state)
