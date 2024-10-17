from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from typing import Dict

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
    # Parse API keys formatted as ABCDEFGHIJKLMNOPQRSTUVWXYZ012345:label
    def parse_keys(self, keys: str) -> Dict[str, str]:
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

    def get_available_keys(self) -> Dict[str, str]:
        keys = self._get_raw_keys()
        if not keys:
            raise HTTPException(status_code=500, detail="No valid API keys available")
        if not keys:
            raise HTTPException(status_code=500, detail="No API keys available")
        keys = self.parse_keys(keys)
        return keys

    # Validate API Key
    def validate_key(self, api_key: str = Security(api_key_header)) -> bool:
        keys = self.get_available_keys()
        if not api_key or api_key not in keys:
            # Print the api keys we have as error
            raise HTTPException(status_code=403, detail=f"Invalid API key {keys}")
        return True

    def _get_raw_keys(self):
        return AppData().get_api_key("fastapi")


# --------------------------
# Trip API
# --------------------------

api_key_handler = ApiKeyHandler()


@app.get("/trips")
@limiter.limit("40/minute")
def get_trips(request: Request, api_key: str = Depends(api_key_handler.validate_key)):
    trips = TripData().get_all()
    return trips
