from datetime import datetime, timedelta

from models.Trip import TripModel
from services.Trip import Trip
from lib.Utils import Utils

from models.Itinerary import DailyItineraryModel, ActivityModel
from models.Weather import ForecastModel, WeatherModel
from models.Attraction import AttractionModel

# --------------------------
# TripData Mocks
# --------------------------

# Dynamic dates
start_date = datetime.now().isoformat()
end_date = (datetime.now() + timedelta(days=2)).isoformat()


def mock_trip_dict() -> dict:
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
                "date": start_date,
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "temperature": None,
                "temperature_min": 23.27,
                "temperature_max": 23.92,
                "weather": "nuvens dispersas",
                "wind_speed": 9.41,
            },
            {
                "timestamp": 1729209600,
                "date": end_date,
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "temperature": None,
                "temperature_min": 23.27,
                "temperature_max": 23.92,
                "weather": "chuva moderada",
                "wind_speed": 9.41,
            },
        ],
        "attractions": [
            {
                "id": "5d609698-9323-4ec3-84f4-fb557ecae7a5",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "name": "Praia do Arrail",
                "url": "https://www.yelp.com/biz/arraial-do-cabo-arraial-do-cabo",
                "review_count": 6,
                "review_stars": 4.7,
                "description": "",
                "image": "https://s3-media0.fl.yelpcdn.com/bphoto/9t3__2a-LlPTLdosAVXgOw/348s.jpg",
            },
            {
                "id": "00000000-0000-4ec3-84f4-fb557ecae7a5",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "name": "Atração Genérica",
                "url": "https://www.yelp.com/biz/arraial-do-cabo-arraial-do-cabo",
                "review_count": 1000,
                "review_stars": 3.0,
                "description": "",
                "image": "https://s3-media0.fl.yelpcdn.com/bphoto/9t3__2a-LlPTLdosAVXgOw/348s.jpg",
            },
        ],
        "itinerary": [
            {
                "date": start_date,
                "title": "Dia 1",
                "items": [
                    {
                        "start_time": "09:00",
                        "end_time": "11:00",
                        "location": "Praia do Arrail - Arraial do Cabo, RJ",
                        "title": "Manhã na Praia do Arrail",
                        "description": "Aproveite a manhã relaxando na Praia do Arrail com nuvens dispersas.",
                    },
                    {
                        "start_time": "11:30",
                        "end_time": "13:00",
                        "location": "Centro de Arraial do Cabo, RJ",
                        "title": "Almoço em Restaurante Local",
                        "description": "Desfrute de pratos tradicionais em um restaurante aconchegante no centro.",
                    },
                ],
            },
            {
                "date": end_date,
                "title": "Dia 2",
                "items": [
                    {
                        "start_time": "09:00",
                        "end_time": "11:00",
                        "location": "Atração Genérica - Arraial do Cabo, RJ",
                        "title": "Exploração da Atração Genérica",
                        "description": "Descubra os encantos locais da Atração Genérica em Arraial do Cabo.",
                    },
                    {
                        "start_time": "11:30",
                        "end_time": "13:00",
                        "location": "Praia dos Anjos - Arraial do Cabo, RJ",
                        "title": "Relaxamento na Praia dos Anjos",
                        "description": "Desfrute do sol e do mar nesta bela praia.",
                    },
                ],
            },
        ],
        "goals": "Conhecer as praias de Arraial do Cabo. \n Aproveitar a gastronomia local.",
        "notes": "This is a test note",
        "tags": ["teste"],
        "summary": "This is a test summary",
        "meta": {
            "feedback": "Nice trip",
            "sentiment": "POSITIVE",
        },
    }


def mock_trip() -> Trip:
    return Trip(trip_data=mock_trip_dict(), save=False)


def mock_trip_model() -> TripModel:
    return mock_trip().model


def mock_trip_csv_new_date():
    trip = mock_trip_dict()
    csv = Trip(trip_data=trip, save=False).to_csv()
    return csv


def mock_trip_csv_old_date():
    trip = mock_trip_dict()
    trip["start_date"] = "2023-11-16T00:00:00"
    trip["end_date"] = "2023-11-17T00:00:00"
    csv = Trip(trip_data=trip, save=False).to_csv()
    return csv


# --------------------------
# Itinerary Mocks
# --------------------------


def mock_itinerary() -> list[DailyItineraryModel]:
    attraction_data = mock_trip_dict()["itinerary"]
    return [DailyItineraryModel(**attraction) for attraction in attraction_data]


def mock_activity():
    activity = mock_itinerary()[0].items[0].model_dump()
    return ActivityModel(**activity)


# --------------------------
# Weather Mocks
# --------------------------


def mock_weather() -> list[ForecastModel]:
    return mock_trip_model().weather


def mock_weather_model() -> ForecastModel:
    return mock_weather()[0]


# --------------------------
# Attraction Mocks
# --------------------------
def mock_attractions() -> list[AttractionModel]:
    attraction_data = mock_trip_dict()["attractions"]
    return [AttractionModel(**attraction) for attraction in attraction_data]


def mock_attraction() -> AttractionModel:
    return mock_attractions()[0]


# --------------------------
# City/State Mocks
# --------------------------


def mock_city_state_json_data():
    return {
        "estados": [
            {
                "nome": "São Paulo",
                "sigla": "SP",
                "cidades": ["São Paulo", "Campinas", "Santos"],
            },
            {
                "nome": "Rio de Janeiro",
                "sigla": "RJ",
                "cidades": ["Rio de Janeiro", "Niterói", "Petropolis"],
            },
        ]
    }


# --------------------------
# AI Gen Itinerary Mocks
# --------------------------


def mock_ai_gen_itinerary_request() -> dict:
    location = (
        mock_trip_model().destination_city + ", " + mock_trip_model().destination_state
    )
    attractions_list = mock_attractions()
    forecast_list = mock_weather()
    start_date = Utils.to_datetime(mock_trip_model().start_date)
    end_date = Utils.to_datetime(mock_trip_model().end_date)
    goals = mock_trip_model().goals

    return dict(
        location=location,
        start_date=start_date,
        end_date=end_date,
        goals=goals,
        forecast_list=forecast_list,
        attractions_list=attractions_list,
    )


def mock_ai_gen_itinerary_response() -> dict:
    return {
        "response": '```json\n[\n  {\n    "date": "2024-11-14",\n    "title": "Dia 1",\n    "items": [\n      {\n        "start_time": "09:00",\n        "end_time": "12:00",\n        "location": "Praia do Arraial - Arraial do Cabo, RJ",\n        "title": "Manhã na Praia do Arraial",\n        "description": "Comece o dia relaxando nas areias brancas da Praia do Arraial, aproveitando o sol e as águas cristalinas. Com o céu com nuvens dispersas, o dia promete ser agradável para um mergulho refrescante ou para simplesmente apreciar a beleza natural da região."\n      },\n      {\n        "start_time": "13:00",\n        "end_time": "15:00",\n        "location": "Atração Genérica - Arraial do Cabo, RJ",\n        "title": "Visita à Atração Genérica",\n        "description": "Após a praia, explore a Atração Genérica, uma atração local que oferece uma experiência única. Aproveite o tempo para conhecer mais sobre a história e a cultura da região."\n      }\n    ]\n  },\n  {\n    "date": "2024-11-15",\n    "title": "Dia 2",\n    "items": [\n      {\n        "start_time": "10:00",\n        "end_time": "12:00",\n        "location": "Praia do Arraial - Arraial do Cabo, RJ",\n        "title": "Caminhada pela Praia do Arraial",\n        "description": "Aproveite a manhã para uma caminhada relaxante pela Praia do Arraial. As condições climáticas podem ser imprevisíveis, mas a beleza natural da praia vale a pena, mesmo com o tempo nublado."\n      },\n      {\n        "start_time": "14:00",\n        "end_time": "17:00",\n        "location": "Atração Genérica - Arraial do Cabo, RJ",\n        "title": "Tarde na Atração Genérica",\n        "description": "Aproveite a tarde para explorar mais a fundo a Atração Genérica. Desfrute de atividades locais, como compras de artesanato ou degustação de pratos típicos da região."\n      }\n    ]\n  },\n  {\n    "date": "2024-11-21",\n    "title": "Dia 3",\n    "items": [\n      {\n        "start_time": "10:00",\n        "end_time": "12:00",\n        "location": "Praia do Arraial - Arraial do Cabo, RJ",\n        "title": "Dia na Praia do Arraial (com chuva)",\n        "description": "Aproveite a manhã para um dia relaxante na Praia do Arraial, mesmo com chuva. A Praia do Arraial é um lugar mágico, e a beleza natural da região é ainda mais encantadora sob a chuva."\n      },\n      {\n        "start_time": "13:00",\n        "end_time": "15:00",\n        "location": "Atração Genérica - Arraial do Cabo, RJ",\n        "title": "Visita à Atração Genérica",\n        "description": "Após a praia, aproveite a tarde para visitar a Atração Genérica. Procure um lugar coberto para se proteger da chuva e desfrutar de um momento cultural."\n      }\n    ]\n  }\n]\n```',
        "provider": "Google Gemini",
    }
