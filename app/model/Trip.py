import uuid
from datetime import datetime
from services.AppData import AppData
from services.LatLong import LatLong


class Trip:
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
    directions: dict
    places: list
    activities: list
    notes: str
    tags: list

    def __init__(self, trip_id: str = None, trip_data: dict = None):
        # If trip_id is provided, load the trip data
        if trip_id is not None:
            self.trip_id = trip_id

            # Load trip data
            if not self._load():
                raise ValueError(
                    f"Trip with ID {self.trip_id} could not be loaded.")
        else:
            self.create(trip_data)

    def create(self, trip_data: dict):
        if trip_data is None:
            raise ValueError("Trip data is required to create a trip.")

        self.trip_id = self._generate_id()
        self.title = trip_data.get("title", "")
        self.origin_city = trip_data.get("origin_city", "")
        self.origin_state = trip_data.get("origin_state", "")

        self.destination_city = trip_data.get("destination_city", "")
        self.destination_state = trip_data.get("destination_state", "")

        self.start_date = trip_data.get("start_date", datetime.now())
        self.end_date = trip_data.get("end_date", datetime.now())
        self.weather = trip_data.get("weather", {})
        self.directions = trip_data.get("directions", {})
        self.places = trip_data.get("places", [])
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

    def update(self, trip_data: dict):
        # Update trip data
        self.title = trip_data.get("title", self.title)
        self.origin_city = trip_data.get("origin_city", self.origin_city)
        self.origin_state = trip_data.get("origin_state", self.origin_state)
        self.destination_city = trip_data.get(
            "destination_city", self.destination_city)
        self.destination_state = trip_data.get(
            "destination_state", self.destination_state)
        self.start_date = trip_data.get("start_date", self.start_date)
        self.end_date = trip_data.get("end_date", self.end_date)
        self.weather = trip_data.get("weather", self.weather)
        self.directions = trip_data.get("directions", self.directions)
        self.places = trip_data.get("places", self.places)
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

    def delete(self):
        return AppData().delete("trip", self.trip_id)

    def _load(self):
        # Fetch trip data from AppData
        TripData = AppData().get("trip", self.trip_id)
        if TripData is None:
            return False

        # Validate trip data before loading
        if not self._validate(TripData):
            raise ValueError(f"Invalid trip data for Trip ID {self.trip_id}")

        # Sanitize the data
        TripData = self._sanitize(TripData)

        # Assign sanitized data to object properties
        self.title = TripData["title"]
        self.origin_city = TripData["origin_city"]
        self.origin_state = TripData["origin_state"]
        self.destination_city = TripData["destination_city"]
        self.destination_state = TripData["destination_state"]

        # If latitude and longitude are not provided, retrieve them using the geocoding API
        if "origin_longitude" not in TripData or "origin_latitude" not in TripData:
            self.origin_longitude, self.origin_latitude = self._get_coordinates(
                self.origin_city, self.origin_state)
        else:
            self.destination_longitude = TripData["destination_longitude"]
            self.destination_latitude = TripData["destination_latitude"]

        if "destination_longitude" not in TripData or "destination_latitude" not in TripData:
            self.destination_longitude, self.destination_latitude = self._get_coordinates(
                self.destination_city, self.destination_state)
        else:
            self.destination_longitude = TripData["destination_longitude"]
            self.destination_latitude = TripData["destination_latitude"]

        self.start_date = TripData["start_date"]
        self.end_date = TripData["end_date"]
        self.weather = TripData.get("weather", {})
        self.directions = TripData.get("directions", {})
        self.places = TripData.get("places", [])
        self.activities = TripData.get("activities", [])
        self.notes = TripData.get("notes", "")
        self.tags = TripData.get("tags", [])

        return True

    def _save(self):
        # Create a dictionary with trip data to save
        TripData = {
            "trip_id": self.trip_id,
            "title": self.title,
            "origin_city": self.origin_city,
            "origin_state": self.origin_state,
            "origin_longitude": self.origin_longitude,
            "origin_latitude": self.origin_latitude,
            "destination_city": self.destination_city,
            "destination_state": self.destination_state,
            "destination_longitude": self.destination_longitude,
            "destination_latitude": self.destination_latitude,
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M"),
            "end_date": self.end_date.strftime("%Y-%m-%d %H:%M"),
            "weather": self.weather,
            "directions": self.directions,
            "places": self.places,
            "activities": self.activities,
            "notes": self.notes,
            "tags": self.tags
        }
        return AppData().save("trip", value=TripData)

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
            datetime.strptime(TripData["start_date"], "%Y-%m-%d %H:%M")
            datetime.strptime(TripData["end_date"], "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format, should be YYYY-MM-DD HH:MM")
            return False

        return True

    def _sanitize(self, TripData):
        # Clean up the data
        TripData["title"] = TripData["title"].strip()

        # Convert start and end dates to datetime objects
        try:
            TripData["start_date"] = datetime.strptime(
                TripData["start_date"], "%Y-%m-%d %H:%M")
            TripData["end_date"] = datetime.strptime(
                TripData["end_date"], "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Dates must be in the format YYYY-MM-DD")

        # Default values for optional fields
        TripData["weather"] = TripData.get("weather", {})
        TripData["directions"] = TripData.get("directions", {})
        TripData["places"] = TripData.get("places", [])
        TripData["activities"] = TripData.get("activities", [])
        TripData["notes"] = TripData.get("notes", "").strip()
        TripData["tags"] = TripData.get("tags", [])

        return TripData

    def _generate_id(self):
        # Generate a unique ID for the trip
        return str(uuid.uuid4())

    def _get_coordinates(self, city, state):
        # Get latitude and longitude using the geocoding API
        return LatLong().get_coordinates(city, state)
