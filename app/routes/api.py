from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from uuid import uuid4

from typing import Dict

from services.Trip import Trip
from services.TripData import TripData
from services.AppData import AppData

# Initialize the rate limiter with a default rate limit
limiter = Limiter(
    key_func=get_remote_address
)  # Use client's IP address for rate limiting

app = FastAPI()

# --------------------------
# Rate Limiting
# --------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --------------------------
# API Key Handling
# --------------------------
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class ApiKeyHandler:
    def parse_keys(self, keys: str) -> list[dict[str, int]]:
        """
        Parse API keys formatted as ABCDEFGHIJKLMNOPQRSTUVWXYZ012345:user_id, ...
        """
        keys = keys.split(",")
        keys_list = []
        for key in keys:
            key = self.parse_key(key)
            if key:
                keys_list.append(key)
        return keys_list

    def parse_key(self, key: str) -> dict[str, int]:
        """
        Parse API key formatted as ABCDEFGHIJKLMNOPQRSTUVWXYZ012345:user_id
        """
        key_parts = key.split(":")

        if len(key_parts) != 2:
            return None

        token, user_id = key_parts

        # Clean invalid characters from token
        _token = "".join(filter(str.isalnum, token))

        # Validate token and user_id
        if _token and len(_token) == 32 and user_id.isnumeric():
            return {_token: int(user_id)}

    def get_available_keys(self) -> list[dict[str, int]]:
        """
        Get available API keys from AppData
        """
        keys = self._get_raw_keys()
        if not keys:
            raise HTTPException(status_code=500, detail="No valid API keys available")
        keys = self.parse_keys(keys)
        return keys

    def validate_key(self, api_key: str = Security(api_key_header)) -> str:
        """
        Validate API key
        """
        keys = self.get_available_keys()
        keys = self._join_keys(keys)
        if not keys:
            raise HTTPException(status_code=500, detail="No valid API keys available")
        if api_key not in keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return api_key

    def get_user_id(self, api_key: str) -> int:
        """
        Get user_id from API key
        """
        keys = self.parse_key(api_key)
        return list(keys.values())[0]

    def _get_raw_keys(self):
        """
        Get raw API keys from AppData
        """
        return AppData().get_api_key("fastapi")

    def _join_keys(self, keys: list[Dict[str, int]]) -> list[str]:
        """
        Join API keys into a list of strings
        """
        return [":".join([k, str(v)]) for key in keys for k, v in key.items()]


# --------------------------
# Trip API
# --------------------------

# Initialize the API key handler
api_key_handler = ApiKeyHandler()


# Create a new trip
@app.post("/trip")
@limiter.limit("10/minute")
def create_user_trip(
    request: Request,
    api_key: str = Depends(api_key_handler.validate_key),
    trip_data: dict = None,
):
    if trip_data is None:
        raise HTTPException(status_code=400, detail="Trip data is required")

    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    # Add user_id to trip_data
    trip_data["user_id"] = user_id

    try:
        trip = Trip(trip_data=trip_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return trip.model


# Get a specific trip
@app.get("/trip/{trip_id}")
@app.get("/trip")
@limiter.limit("20/minute")
def get_user_trip(
    request: Request,
    trip_id: str = None,
    api_key: str = Depends(api_key_handler.validate_key),
):
    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    trip = TripData().get_user_trip(trip_id=trip_id, user_id=user_id)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    return trip


# Get all user trips
@app.get("/trips")
@limiter.limit("40/minute")
def get_user_trips(
    request: Request,
    api_key: str = Depends(api_key_handler.validate_key),
    limit: int = 10,
):
    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    if limit < 0:
        limit = 0

    trips = TripData().get_user_trips(user_id=user_id, limit=limit)

    if not trips:
        raise HTTPException(status_code=404, detail="No trips found")

    return trips
