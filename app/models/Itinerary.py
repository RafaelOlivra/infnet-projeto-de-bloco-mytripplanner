from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date, time
from typing import List, Optional


class ActivityModel(BaseModel):
    start_time: time
    end_time: time
    location: str
    title: str
    description: Optional[str] = None

    # Validator to ensure end_time is after start_time
    @model_validator(mode="after")
    def check_time_order(cls, field_values):
        end_time = field_values.end_time
        start_time = field_values.start_time
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be later than start_time")
        return field_values


class DailyItineraryModel(BaseModel):
    date: datetime | date | str
    title: str
    items: List[ActivityModel]

    @field_validator("date")
    def convert_to_datetime(cls, value):
        """
        Convert date to datetime if necessary.
        """
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)

        return value
