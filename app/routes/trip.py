import fastapi
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from services.Trip import Trip
from services.TripData import TripData

app = fastapi.FastAPI()
