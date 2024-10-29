from fastapi import FastAPI, HTTPException, Depends, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from models.Trip import TripModel

from services.Trip import Trip
from services.TripData import TripData
from services.ApiKeyHandler import ApiKeyHandler

app = FastAPI()

# --------------------------
# Rate Limiting
# --------------------------
# Use client's IP address for rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# --------------------------
# API Key Handling
# --------------------------
api_key_handler = ApiKeyHandler()
api_key_header = api_key_handler.header


# --------------------------
# Trip API
# --------------------------
# Create a new trip
@app.post("/trip")
@limiter.limit("10/minute")
async def create_user_trip(
    request: Request,
    trip_data: TripModel,
    api_key: str = Depends(api_key_handler.validate_key),
) -> TripModel:

    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    # Add user_id to trip_data
    trip_data = trip_data.model_dump()
    trip_data["user_id"] = user_id

    try:
        trip = Trip(trip_data=trip_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return trip.model


# Get a specific trip
# @app.get("/trip")
@app.get("/trip/{trip_id}")
@limiter.limit("20/minute")
async def get_user_trip(
    request: Request,
    trip_id: str,
    api_key: str = Depends(api_key_handler.validate_key),
) -> TripModel:
    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    trip = TripData().get_user_trip(trip_id=trip_id, user_id=user_id)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    return trip


# Get all user trips
@app.get("/trips")
@limiter.limit("40/minute")
async def get_user_trips(
    request: Request,
    limit: int = 10,
    api_key: str = Depends(api_key_handler.validate_key),
) -> list[TripModel]:
    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    if limit < 0:
        limit = 0

    trips = TripData().get_user_trips(user_id=user_id, limit=limit)

    if not trips:
        raise HTTPException(status_code=404, detail="No trips found")

    return trips


# Delete a specific trip
# @app.delete("/trip")
@app.delete("/trip/{trip_id}")
@limiter.limit("10/minute")
async def delete_user_trip(
    request: Request,
    trip_id: str,
    api_key: str = Depends(api_key_handler.validate_key),
):
    # Get user_id from API key
    user_id = api_key_handler.get_user_id(api_key)

    trip_model = TripData().get_user_trip(trip_id=trip_id, user_id=user_id)
    trip = Trip().from_model(trip_model)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.delete():
        return {"detail": "Trip deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete trip")
