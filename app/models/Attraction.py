import uuid
from pydantic import BaseModel, HttpUrl, Field, conint, confloat


class Attraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    city_name: str
    state_name: str
    name: str
    url: HttpUrl
    review_count: conint(ge=0) = Field(default=0)
    review_stars: confloat(ge=0, le=5) = Field(default=0)
    description: str
    image: HttpUrl
