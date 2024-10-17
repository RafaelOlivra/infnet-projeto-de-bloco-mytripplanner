import uuid

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import List, Optional

from models.Weather import ForecastModel
from models.Weather import ForecastModel
from models.Attraction import AttractionModel


class TripModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0  # For future use
    created_at: datetime | date | str = Field(default_factory=datetime.now)
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
    start_date: datetime | date | str
    end_date: datetime | date | str
    weather: Optional[List[ForecastModel]] = None
    attractions: Optional[List[AttractionModel]] = None
    goals: str = ""
    notes: str = ""
    tags: List[str] = Field(default_factory=list)

    @field_validator("created_at", "start_date", "end_date")
    def convert_to_datetime(cls, value):
        """
        Convert date to datetime if necessary.
        """
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        return value

    def __getitem__(self, attribute: str):
        return self.__getattribute__(attribute)
