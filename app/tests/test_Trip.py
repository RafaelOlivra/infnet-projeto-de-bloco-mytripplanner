import json
import pytest
import time
from datetime import datetime, timedelta

from unittest.mock import patch
from services.Trip import Trip
from services.TripData import TripData


# Mock trip data for testing
start_date = datetime.now().isoformat()
end_date = (datetime.now() + timedelta(days=7)).isoformat()


def mock_trip_data() -> dict:
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "user_id": 0,
        "created_at": "2024-10-15T00:00:00",
        "slug": "teste",
        "title": "Teste",
        "origin_city": "\u00c1guas de Santa B\u00e1rbara",
        "origin_state": "SP",
        "origin_longitude": -22.8812164,
        "origin_latitude": -49.2397734,
        "destination_city": "Arraial do Cabo",
        "destination_state": "RJ",
        "destination_longitude": -22.9667613,
        "destination_latitude": -42.0277716,
        "travel_by": "driving",
        "start_date": start_date,
        "end_date": end_date,
        "weather": [
            {
                "timestamp": 1729026000,
                "date": "2024-10-17T00:00:00",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "temperature": None,
                "temperature_min": 23.27,
                "temperature_max": 23.92,
                "weather": "nuvens dispersas",
                "wind_speed": 9.41,
            },
        ],
        "attractions": [
            {
                "id": "5d609698-9323-4ec3-84f4-fb557ecae7a5",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "name": "Arraial do Cabo",
                "url": "https://www.yelp.com/biz/arraial-do-cabo-arraial-do-cabo",
                "review_count": 6,
                "review_stars": 4.7,
                "description": "",
                "image": "https://s3-media0.fl.yelpcdn.com/bphoto/9t3__2a-LlPTLdosAVXgOw/348s.jpg",
            },
        ],
        "goals": "Test",
        "notes": "This is a test note",
        "tags": ["teste"],
    }


def mock_trip_csv():
    return f"""id,user_id,created_at,slug,title,origin_city,origin_state,origin_longitude,origin_latitude,destination_city,destination_state,destination_longitude,destination_latitude,travel_by,start_date,end_date,goals,notes,tags,weather_base64,attractions_base64
0000000-0000-0000-0000-000000000000,0,2024-10-15T00:00:00,viagem-a-angra-dos-reis,Viagem à Angra dos Reis,Sorocaba,SP,-23.4709096,-47.4851438,Angra dos Reis,RJ,-23.0069216,-44.3185172,driving,{start_date},{end_date},Conhecer a cidade,Conhecer as praias,passeio____COMMA____praia____COMMA____sol,W3sidGltZXN0YW1wIjogMTcyOTAwNDQwMCwgImRhdGUiOiAiMjAyNC0xMC0xNVQwMDowMDowMCIsICJjaXR5X25hbWUiOiAiQW5ncmEgZG9zIFJlaXMiLCAic3RhdGVfbmFtZSI6ICJSSiIsICJ0ZW1wZXJhdHVyZSI6IG51bGwsICJ0ZW1wZXJhdHVyZV9taW4iOiAyMC4xOSwgInRlbXBlcmF0dXJlX21heCI6IDIzLjc3LCAid2VhdGhlciI6ICJudWJsYWRvIiwgIndpbmRfc3BlZWQiOiAxLjgxfSwgeyJ0aW1lc3RhbXAiOiAxNzI5MDQ3NjAwLCAiZGF0ZSI6ICIyMDI0LTEwLTE2VDAwOjAwOjAwIiwgImNpdHlfbmFtZSI6ICJBbmdyYSBkb3MgUmVpcyIsICJzdGF0ZV9uYW1lIjogIlJKIiwgInRlbXBlcmF0dXJlIjogbnVsbCwgInRlbXBlcmF0dXJlX21pbiI6IDE5LjY0LCAidGVtcGVyYXR1cmVfbWF4IjogMjUuMjksICJ3ZWF0aGVyIjogIm51YmxhZG8iLCAid2luZF9zcGVlZCI6IDEuNzYxMjV9LCB7InRpbWVzdGFtcCI6IDE3MjkxMzQwMDAsICJkYXRlIjogIjIwMjQtMTAtMTdUMDA6MDA6MDAiLCAiY2l0eV9uYW1lIjogIkFuZ3JhIGRvcyBSZWlzIiwgInN0YXRlX25hbWUiOiAiUkoiLCAidGVtcGVyYXR1cmUiOiBudWxsLCAidGVtcGVyYXR1cmVfbWluIjogMjAuNzQsICJ0ZW1wZXJhdHVyZV9tYXgiOiAyNC45NywgIndlYXRoZXIiOiAibnVibGFkbyIsICJ3aW5kX3NwZWVkIjogMS41NTI1fSwgeyJ0aW1lc3RhbXAiOiAxNzI5MjIwNDAwLCAiZGF0ZSI6ICIyMDI0LTEwLTE4VDAwOjAwOjAwIiwgImNpdHlfbmFtZSI6ICJBbmdyYSBkb3MgUmVpcyIsICJzdGF0ZV9uYW1lIjogIlJKIiwgInRlbXBlcmF0dXJlIjogbnVsbCwgInRlbXBlcmF0dXJlX21pbiI6IDIxLjc2LCAidGVtcGVyYXR1cmVfbWF4IjogMjUuNywgIndlYXRoZXIiOiAibnVibGFkbyIsICJ3aW5kX3NwZWVkIjogMS42MjV9LCB7InRpbWVzdGFtcCI6IDE3MjkzMDY4MDAsICJkYXRlIjogIjIwMjQtMTAtMTlUMDA6MDA6MDAiLCAiY2l0eV9uYW1lIjogIkFuZ3JhIGRvcyBSZWlzIiwgInN0YXRlX25hbWUiOiAiUkoiLCAidGVtcGVyYXR1cmUiOiBudWxsLCAidGVtcGVyYXR1cmVfbWluIjogMjIuMSwgInRlbXBlcmF0dXJlX21heCI6IDI0LjAzLCAid2VhdGhlciI6ICJjaHV2YSBsZXZlIiwgIndpbmRfc3BlZWQiOiAxLjE0NzV9LCB7InRpbWVzdGFtcCI6IDE3MjkzOTMyMDAsICJkYXRlIjogIjIwMjQtMTAtMjBUMDA6MDA6MDAiLCAiY2l0eV9uYW1lIjogIkFuZ3JhIGRvcyBSZWlzIiwgInN0YXRlX25hbWUiOiAiUkoiLCAidGVtcGVyYXR1cmUiOiBudWxsLCAidGVtcGVyYXR1cmVfbWluIjogMjIuMiwgInRlbXBlcmF0dXJlX21heCI6IDIyLjgyLCAid2VhdGhlciI6ICJjaHV2YSBmb3J0ZSIsICJ3aW5kX3NwZWVkIjogMS4yMDc1fV0=,W3siaWQiOiAiZGM5MGE1OTktMjY5NS00MGNkLTljYTItMmY3OTkzNGY5YTY5IiwgImNpdHlfbmFtZSI6ICJBbmdyYSBkb3MgUmVpcyIsICJzdGF0ZV9uYW1lIjogIlJKIiwgIm5hbWUiOiAiQmFyIGRvIEx1aXoiLCAidXJsIjogImh0dHBzOi8vd3d3LnllbHAuY29tL2Jpei9iYXItZG8tbHVpei1hbmdyYS1kb3MtcmVpcyIsICJyZXZpZXdfY291bnQiOiAyLCAicmV2aWV3X3N0YXJzIjogNC4wLCAiZGVzY3JpcHRpb24iOiAiIiwgImltYWdlIjogImh0dHBzOi8vczMtbWVkaWEwLmZsLnllbHBjZG4uY29tL2JwaG90by83eWF1bkx2eGI3cDBCY2djR2t5RVZ3LzM0OHMuanBnIn0sIHsiaWQiOiAiN2M1YWQ3ZDAtYTEyOC00NDFmLWI3ZDgtNmMwMjI1NTdiNjhjIiwgImNpdHlfbmFtZSI6ICJBbmdyYSBkb3MgUmVpcyIsICJzdGF0ZV9uYW1lIjogIlJKIiwgIm5hbWUiOiAiUHJhaWEgZGEgUGFybmFpb2NhIiwgInVybCI6ICJodHRwczovL3d3dy55ZWxwLmNvbS9iaXovcHJhaWEtZGEtcGFybmFpb2NhLWFuZ3JhLWRvcy1yZWlzIiwgInJldmlld19jb3VudCI6IDIsICJyZXZpZXdfc3RhcnMiOiA1LjAsICJkZXNjcmlwdGlvbiI6ICIiLCAiaW1hZ2UiOiAiaHR0cHM6Ly9zMy1tZWRpYTAuZmwueWVscGNkbi5jb20vYnBob3RvL2JzYUFpM3ZhXy00V2h4SmNtV0xTRlEvMzQ4cy5qcGcifV0=
"""


# Test creating a new trip
@patch("services.TripData.AppData.save")
def test_create_trip(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data())

    # Check if the trip was created correctly
    assert trip.get("slug") == mock_trip_data()["slug"]


# Test getting a property from the trip
@patch("services.TripData.AppData.save")
def test_get_trip_property(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data())

    # Check if the property is correct
    assert trip.get("title") == "Teste"


# Test updating a trip
@patch("services.TripData.AppData.save")
def test_update_trip(app_data_save_mock):

    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data())

    # Update the trip
    trip.update({"title": "Updated title"})

    # Check if the trip was updated correctly
    assert trip.model.title == "Updated title"


# Test deleting a trip
def test_delete_trip():
    # Create a new trip
    trip = Trip(trip_data=mock_trip_data())

    # Delete the trip
    trip_id = trip.get("id")
    trip.delete()

    # Check if the trip was deleted correctly
    assert TripData().get(trip_id=trip_id) is None


@patch("services.TripData.AppData.save")
def test_import_trip_csv(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip().from_csv(mock_trip_csv())

    # Check if the trip was imported correctly
    assert trip["slug"] == "viagem-a-angra-dos-reis"


@patch("services.TripData.AppData.save")
def test_import_trip_json(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    trip = Trip().from_csv(mock_trip_csv())
    json_data = trip.to_json()

    # Create a new trip
    trip = Trip().from_json(json_data)

    # Check if the trip was imported correctly
    assert trip["slug"] == "viagem-a-angra-dos-reis"
