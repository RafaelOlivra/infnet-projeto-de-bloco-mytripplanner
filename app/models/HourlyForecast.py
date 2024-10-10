from pydantic import BaseModel
from typing import Optional


class HourlyForecast(BaseModel):
    timestamp: int
    date: str
    city_name: str
    state_name: str
    temperature: float
    weather: str
    wind_speed: float
