import fastapi
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from models.Trip import Trip
from services.TripData import TripData

