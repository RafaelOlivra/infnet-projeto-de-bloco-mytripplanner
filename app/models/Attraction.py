import uuid
from pydantic import BaseModel, HttpUrl, Field, conint, confloat, field_validator
from datetime import datetime, date, timedelta
from typing import List, Optional


class AttractionModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[datetime | date | str] = Field(
        default_factory=lambda: datetime.now() - timedelta(days=30)
    )
    city_name: str
    state_name: str
    name: str
    url: HttpUrl
    review_count: conint(ge=0) = Field(default=0)  # type: ignore
    review_stars: confloat(ge=-1, le=5) = Field(default=0)  # type: ignore
    description: str
    image: HttpUrl

    @field_validator("created_at")
    def convert_to_datetime(cls, value):
        """
        Convert date to datetime if necessary.
        """
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        return value
