from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from typing import Dict

from services.TripData import TripData
from services.AppData import AppData

app = FastAPI()

# --------------------------
# API Key Handling
# --------------------------
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Parse API keys formatted as ABCDEFGHIJKLMNOPQRSTUVWXYZ012345:label
def parse_api_keys(keys: str) -> Dict[str, str]:
    keys = keys.split(",")
    keys_dict = {}
    for key in keys:
        key_parts = key.split(":")
        if len(key_parts) != 2:
            continue  # Skip if the format is invalid (missing label)

        token, label = key_parts

        # Clean invalid characters from token
        _token = "".join(filter(str.isalnum, token))

        # Ensure both token and label are alphanumeric and token is 32 characters
        if _token and len(_token) == 32 and label.isalnum():
            keys_dict[_token] = label

    return keys_dict


def get_available_api_keys() -> Dict[str, str]:
    keys = AppData().get_api_key("fastapi")
    if not keys:
        raise HTTPException(status_code=500, detail="No API keys available")
    keys = parse_api_keys(keys)
    if not keys:
        raise HTTPException(status_code=500, detail="No valid API keys available")
    return keys


# Validate API Key
def validate_api_key(api_key: str = Security(api_key_header)) -> None:
    keys = get_available_api_keys()
    if not api_key or api_key not in keys:
        raise HTTPException(status_code=403, detail="Invalid API key")


# --------------------------
# Trip API
# --------------------------


# Get all trips by user
@app.get("/trips")
def get_trips(api_key: str = Depends(validate_api_key)):
    trips = TripData().get_all()
    return trips
