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
    def parse_keys(self, keys: str) -> list[Dict[str, int]]:
        keys = keys.split(",")
        keys_list = []
        for key in keys:
            key = self.parse_key(key)
            if key:
                keys_list.append(key)
        return keys_list

    def parse_key(self, key: str) -> Dict[str, int]:
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

    def get_available_keys(self) -> list[Dict[str, int]]:
        keys = self._get_raw_keys()
        if not keys:
            raise HTTPException(status_code=500, detail="No valid API keys available")
        keys = self.parse_keys(keys)
        return keys

    def validate_key(self, api_key: str = Security(api_key_header)) -> bool:
        """
        Validate API key
        """
        keys = self.get_available_keys()
        keys = self._join_keys(keys)
        if not keys:
            raise HTTPException(status_code=500, detail="No valid API keys available")
        if api_key not in keys:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return True

    def _get_raw_keys(self):
        return AppData().get_api_key("fastapi")

    def _join_keys(self, keys: list[Dict[str, int]]) -> list[str]:
        return [":".join([k, str(v)]) for key in keys for k, v in key.items()]


# --------------------------
# Trip API
# --------------------------

api_key_handler = ApiKeyHandler()


@app.get("/trips")
@limiter.limit("40/minute")
def get_user_trips(
    request: Request,
    api_key: str = Depends(api_key_handler.validate_key),
    user_id: int = None,
    limit: int = 10,
):
    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID is required")

    if limit < 0:
        limit = 0

    trips = TripData().get_all(user_id=user_id, limit=limit)
    return trips
