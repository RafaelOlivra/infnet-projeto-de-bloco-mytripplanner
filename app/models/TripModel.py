from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import List, Dict, Optional
import uuid


class TripModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    travel_by: str = "driving"
    start_date: datetime
    end_date: datetime
    weather: Optional[List[Dict[str, str | None]]] = Field(default_factory=list)
    goals: str = ""
    activities: str = ""
    notes: str = ""
    tags: List[str] = Field(default_factory=list)

    @validator("start_date", "end_date", pre=True)
    def convert_to_datetime(cls, value):
        """
        Convert date to datetime if necessary.
        """
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        return value

    class Config:
        arbitrary_types_allowed = True
