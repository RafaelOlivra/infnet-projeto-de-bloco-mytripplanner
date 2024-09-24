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
        # If trip_id is provided, load the trip data
        if id is not None:
            self.id = id

            # Load trip data
            if not self._load():
                raise ValueError(
                    f"Trip with ID {self.id} could not be loaded.")
        elif trip_data is not None:
            self.create(trip_data)

    def create(self, trip_data: dict):
        if trip_data is None:
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

        # If latitude and longitude are provided, use them,
        # otherwise, retrieve them using the geocoding API
        if "origin_longitude" in trip_data and "origin_latitude" in trip_data:
            self.origin_longitude = trip_data["origin_longitude"]
            self.origin_latitude = trip_data["origin_latitude"]
        else:
            self.origin_longitude, self.origin_latitude = self._get_coordinates(
                self.origin_city, self.origin_state)

        if "destination_longitude" in trip_data and "destination_latitude" in trip_data:
            self.destination_longitude = trip_data["destination_longitude"]
            self.destination_latitude = trip_data["destination_latitude"]
        else:
            self.destination_longitude, self.destination_latitude = self._get_coordinates(
                self.destination_city, self.destination_state)

        # Get weather data for the trip
        self.weather = OpenWeatherMap().get_forecast_for_next_5_days(
            self.destination_city, self.destination_state)

        return self._save()

    def update(self, trip_data: dict):
        # Update trip data
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

        # Update the coordinates if the origin or destination city/state has changed
        if trip_data.get("origin_city", self.origin_city) != self.origin_city or trip_data.get("origin_state", self.origin_state) != self.origin_state:
            self.origin_city = trip_data.get("origin_city", self.origin_city)
            self.origin_state = trip_data.get(
                "origin_state", self.origin_state)
            self._update_coordinates()

        if trip_data.get("destination_city", self.destination_city) != self.destination_city or trip_data.get("destination_state", self.destination_state) != self.destination_state:
            self.destination_city = trip_data.get(
                "destination_city", self.destination_city)
            self.destination_state = trip_data.get(
                "destination_state", self.destination_state)
            self._update_coordinates()

        return self

    def export(self, to="CSV"):
        """
        Export trip data to a file.
        """
        if to == "CSV":
            return self.to_csv()
        elif to == "JSON":
            return self.to_json()
        else:
            raise ValueError("Invalid export format.")

    def delete(self):
        return TripData().delete(self.id)

    def _load(self):
        # Fetch trip data from TripData
        Trip = TripData().get_trip_data(self.id)

        if Trip is None:
            return False

        # Validate trip data before loading
        if not self._validate(Trip):
            raise ValueError(f"Invalid trip data for Trip ID {self.id}")

        # Sanitize the data
        Trip = self._sanitize(Trip)

        # Assign sanitized data to object properties
        self.title = Trip["title"]
        self.slug = Trip["slug"] if "slug" in Trip else Utils().slugify(
            self.title)
        self.origin_city = Trip["origin_city"]
        self.origin_state = Trip["origin_state"]
        self.destination_city = Trip["destination_city"]
        self.destination_state = Trip["destination_state"]

        # If latitude and longitude are not provided, retrieve them using the geocoding API
        if "origin_longitude" not in Trip or "origin_latitude" not in Trip:
            self.origin_longitude, self.origin_latitude = self._get_coordinates(
                self.origin_city, self.origin_state)
        else:
            self.origin_longitude = Trip["origin_longitude"]
            self.origin_latitude = Trip["origin_latitude"]

        if "destination_longitude" not in Trip or "destination_latitude" not in Trip:
            self.destination_longitude, self.destination_latitude = self._get_coordinates(
                self.destination_city, self.destination_state)
        else:
            self.destination_longitude = Trip["destination_longitude"]
            self.destination_latitude = Trip["destination_latitude"]

        self.start_date = Trip["start_date"]
        self.end_date = Trip["end_date"]
        self.weather = Trip.get("weather", {})
        self.goals = Trip.get("goals", "")
        self.activities = Trip.get("activities", [])
        self.notes = Trip.get("notes", "")
        self.tags = Trip.get("tags", [])

        return True

    def _save(self):
        if TripData().save(value=self.to_json(), id=self.id):
            return self
        return False

    def _get_trip_data_object(self):
        # Create a dictionary with trip data
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

    def to_json(self):
        # Convert the trip data to a JSON string
        return json.dumps(self._get_trip_data_object())

    def to_csv(self):
        # Load the JSON string
        data = json.loads(self.to_json())

        # Serialize weather data to base64
        weather_data = data["weather"]
        weather_data = base64.b64encode(
            json.dumps(weather_data).encode()).decode()
        # Add _base64 suffix to the weather column
        data["weather_base64"] = weather_data
        del data["weather"]

        # Make sure the goals are a string
        data["tags"] = ", ".join(data["tags"])

        # Scape any special characters on all fields
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace("\n", " ")

        # Create a CSV file with the trip data
        csv_data = StringIO()
        writer = csv.DictWriter(csv_data, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

        return csv_data.getvalue()

    def from_json(self, json_string):
        # Load the JSON string
        data = json.loads(json_string)

        # Add [Imported] to the title
        data["title"] = f"[Importado] {data['title']}"

        # Generate a new trip ID
        data["trip_id"] = self._generate_id()

        # Return a new Trip object with the loaded data
        return Trip(trip_data=data)

    def from_csv(self, csv_data):
        # Load the CSV data
        reader = csv.DictReader(StringIO(csv_data))
        header = reader.fieldnames
        data = next(reader)

        # Deserialize weather data from base64
        weather_data = data["weather_base64"]
        weather_data = base64.b64decode(weather_data).decode()
        data["weather"] = json.loads(weather_data)
        del data["weather_base64"]

        # Convert tags to a list
        data["tags"] = [tag.strip() for tag in data["tags"].split(",")]

        # Add [Imported] to the title
        data["title"] = f"[Importado] {data['title']}"

        # Generate a new trip ID
        data["trip_id"] = self._generate_id()

        # Return a new Trip object with the loaded data
        return Trip(trip_data=data)

    def _update_coordinates(self):
        # Update the latitude and longitude for the origin and destination cities
        self.origin_longitude, self.origin_latitude = self._get_coordinates(
            self.origin_city, self.origin_state)
        self.destination_longitude, self.destination_latitude = self._get_coordinates(
            self.destination_city, self.destination_state)

        # Update the trip data with the new coordinates
        return self._save()

    def _validate(self, TripData):
        # Required fields validation
        required_fields = ["title", "origin_city", "origin_state",
                           "destination_city", "destination_state", "start_date", "end_date"]
        for field in required_fields:
            if field not in TripData or not TripData[field]:
                print(f"Missing or empty field: {field}")
                return False

        # Validate date format
        try:
            datetime.strptime(TripData["start_date"], self._get_time_format())
            datetime.strptime(TripData["end_date"], self._get_time_format())
        except ValueError:
            print("Invalid date format, should be YYYY-MM-DD HH:MM")
            return False

        return True

    def _sanitize(self, TripData):
        # Clean up the data
        TripData["title"] = TripData["title"].strip()

        # Convert start and end dates to datetime objects and format them
        # back to the expected format (YYYY-MM-DD HH:MM) string
        try:
            TripData["start_date"] = datetime.strptime(
                TripData["start_date"], self._get_time_format()).strftime(self._get_time_format())
            TripData["end_date"] = datetime.strptime(
                TripData["end_date"], self._get_time_format()).strftime(self._get_time_format())
        except ValueError:
            raise ValueError("Dates must be in the format YYYY-MM-DD HH:MM")

        # Default values for optional fields
        TripData["weather"] = TripData.get("weather", {})
        TripData["activities"] = TripData.get("activities", [])
        TripData["tags"] = TripData.get("tags", [])

        # Make sure goals and notes are texts with no weird characters
        TripData["goals"] = TripData["goals"].strip()
        TripData["notes"] = TripData["notes"].strip()

        return TripData

    def _generate_id(self):
        # Generate a unique ID for the trip
        return str(uuid.uuid4())

    def _get_time_format(self):
        return "%Y-%m-%d %H:%M"

    def _get_coordinates(self, city, state):
        # Get latitude and longitude using the geocoding API
        return LatLong().get_coordinates(city, state)
