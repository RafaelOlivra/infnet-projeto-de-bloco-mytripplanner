from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date

from lib.Utils import Utils


class ForecastModel(BaseModel):
    timestamp: int
    date: datetime | date | str
    city_name: str
    state_name: str
    temperature: Optional[float]
    temperature_min: Optional[float]
    temperature_max: Optional[float]
    weather: str
    wind_speed: float

    @field_validator("date")
    def convert_to_datetime(cls, value):
        """Convert date to datetime if necessary."""
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        if isinstance(value, str):
            return Utils.to_datetime(value)
        return value


class WeatherModel(BaseModel):
    city: Optional[str]
    country: Optional[str]
    coordinates: Optional[str]
    temperature_k: Optional[float]  # Temperature in Kelvin
    feels_like_k: Optional[float]  # Feels like temperature in Kelvin
    temperature_min_k: Optional[float]  # Minimum temperature in Kelvin
    temperature_max_k: Optional[float]  # Maximum temperature in Kelvin
    pressure_hpa: Optional[int]  # Pressure in hPa
    humidity_percent: Optional[int]  # Humidity percentage
    visibility_m: Optional[int]  # Visibility in meters
    wind_speed_ms: Optional[float]  # Wind speed in meters/second
    wind_direction_deg: Optional[int]  # Wind direction in degrees
    wind_gust_ms: Optional[float]  # Wind gust in meters/second
    cloudiness_percent: Optional[int]
    weather: Optional[str]  # Main weather description
    weather_description: Optional[str]  # Detailed weather description
    sunrise_utc: Optional[int]
    sunset_utc: Optional[int]
    timezone_s: Optional[int]
    timestamp_dt: Optional[int]
