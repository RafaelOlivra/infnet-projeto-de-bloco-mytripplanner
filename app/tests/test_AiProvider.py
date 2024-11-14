from lib.Utils import Utils

import pytest

from services.AiProvider import AiProvider
from services.Logger import _log
from services.HuggingFaceProvider import HuggingFaceProvider
from services.GeminiProvider import GeminiProvider

from tests.test_Trip import mock_trip_model, mock_trip
from tests.test_Itinerary import mock_activity, mock_itinerary
from tests.test_Attractions import mock_attractions


def mock_weather():
    return mock_trip_model().weather


def mock_itinerary_gen_request() -> dict:
    location = (
        mock_trip_model().destination_city + ", " + mock_trip_model().destination_state
    )
    attractions_list = mock_attractions()
    forecast_list = mock_weather()
    start_date = Utils.to_datetime(mock_trip_model().start_date)
    end_date = Utils.to_datetime(mock_trip_model().end_date)

    return dict(
        location=location,
        start_date=start_date,
        end_date=end_date,
        forecast_list=forecast_list,
        attractions_list=attractions_list,
    )


def mock_ai_provider_response() -> dict:
    return {
        "response": '```json\n[\n  {\n    "date": "2024-11-14",\n    "title": "Dia 1",\n    "items": [\n      {\n        "start_time": "09:00",\n        "end_time": "12:00",\n        "location": "Praia do Arraial - Arraial do Cabo, RJ",\n        "title": "Manhã na Praia do Arraial",\n        "description": "Comece o dia relaxando nas areias brancas da Praia do Arraial, aproveitando o sol e as águas cristalinas. Com o céu com nuvens dispersas, o dia promete ser agradável para um mergulho refrescante ou para simplesmente apreciar a beleza natural da região."\n      },\n      {\n        "start_time": "13:00",\n        "end_time": "15:00",\n        "location": "Atração Genérica - Arraial do Cabo, RJ",\n        "title": "Visita à Atração Genérica",\n        "description": "Após a praia, explore a Atração Genérica, uma atração local que oferece uma experiência única. Aproveite o tempo para conhecer mais sobre a história e a cultura da região."\n      }\n    ]\n  },\n  {\n    "date": "2024-11-15",\n    "title": "Dia 2",\n    "items": [\n      {\n        "start_time": "10:00",\n        "end_time": "12:00",\n        "location": "Praia do Arraial - Arraial do Cabo, RJ",\n        "title": "Caminhada pela Praia do Arraial",\n        "description": "Aproveite a manhã para uma caminhada relaxante pela Praia do Arraial. As condições climáticas podem ser imprevisíveis, mas a beleza natural da praia vale a pena, mesmo com o tempo nublado."\n      },\n      {\n        "start_time": "14:00",\n        "end_time": "17:00",\n        "location": "Atração Genérica - Arraial do Cabo, RJ",\n        "title": "Tarde na Atração Genérica",\n        "description": "Aproveite a tarde para explorar mais a fundo a Atração Genérica. Desfrute de atividades locais, como compras de artesanato ou degustação de pratos típicos da região."\n      }\n    ]\n  },\n  {\n    "date": "2024-11-21",\n    "title": "Dia 3",\n    "items": [\n      {\n        "start_time": "10:00",\n        "end_time": "12:00",\n        "location": "Praia do Arraial - Arraial do Cabo, RJ",\n        "title": "Dia na Praia do Arraial (com chuva)",\n        "description": "Aproveite a manhã para um dia relaxante na Praia do Arraial, mesmo com chuva. A Praia do Arraial é um lugar mágico, e a beleza natural da região é ainda mais encantadora sob a chuva."\n      },\n      {\n        "start_time": "13:00",\n        "end_time": "15:00",\n        "location": "Atração Genérica - Arraial do Cabo, RJ",\n        "title": "Visita à Atração Genérica",\n        "description": "Após a praia, aproveite a tarde para visitar a Atração Genérica. Procure um lugar coberto para se proteger da chuva e desfrutar de um momento cultural."\n      }\n    ]\n  }\n]\n```',
        "provider": "Google Gemini",
    }


# --------------------------
# AiProvider Tests
# --------------------------
def test_generate_weather_summary():
    ai_provider = AiProvider()

    itinerary_request = mock_itinerary_gen_request()
    forecast_list = itinerary_request["forecast_list"]

    summary = ai_provider._generate_weather_summary(
        forecast_list=forecast_list,
        start_date=itinerary_request["start_date"],
        end_date=itinerary_request["end_date"],
    )

    date = Utils.to_datetime(forecast_list[0].date).isoformat()
    test_summary = date + " - " + forecast_list[0].weather

    assert test_summary in summary
    assert "chuva moderada" in summary
    assert "Não há dados do tempo" in summary


def test_empty_generate_weather_summary():
    ai_provider = AiProvider()
    itinerary_request = mock_itinerary_gen_request()
    forecast_list = None

    summary = ai_provider._generate_weather_summary(
        forecast_list=forecast_list,
        start_date=itinerary_request["start_date"],
        end_date=itinerary_request["end_date"],
    )

    test_summary = "* Não há dados do tempo disponíveis"

    assert test_summary in summary


def test_generate_attractions_summary():
    ai_provider = AiProvider()
    attractions_list = mock_itinerary_gen_request()["attractions_list"]

    summary = ai_provider._generate_attractions_summary(
        attractions_list=attractions_list
    )

    test_summary = (
        "* "
        + attractions_list[0].name
        + " - "
        + attractions_list[0].city_name
        + ", "
        + attractions_list[0].state_name
    )

    assert test_summary in summary


def test_empty_generate_attractions_summary():
    ai_provider = AiProvider()
    summary = ai_provider._generate_attractions_summary(attractions_list=None)

    test_summary = "* Não há atrações disponíveis"

    assert test_summary in summary


def test_generate_final_prompt():
    ai_provider = AiProvider()
    itinerary_request = mock_itinerary_gen_request()

    ai_provider.prepare(**itinerary_request)

    prompt = ai_provider._generate_final_prompt()

    # Check for the presence of the test strings

    # Location
    assert itinerary_request["location"] in prompt

    # Weather summary
    forecast_item = itinerary_request["forecast_list"][0]
    date = Utils.to_datetime(forecast_item.date).isoformat()
    test_summary = date + " - " + forecast_item.weather
    assert test_summary in prompt

    # Attractions summary
    attraction_item = itinerary_request["attractions_list"][0]
    test_summary = (
        "* "
        + attraction_item.name
        + " - "
        + attraction_item.city_name
        + ", "
        + attraction_item.state_name
    )
    assert test_summary in prompt


def test_itinerary_conversion():
    ai_provider = AiProvider()
    response = mock_ai_provider_response()

    # Test the json conversion
    itinerary = ai_provider._to_json(response)
    _log(itinerary, level="DEBUG")

    # Test the itinerary conversion
    itinerary = ai_provider._to_itinerary(response)
    _log(itinerary, level="DEBUG")


# --------------------------
# HuggingFaceProvider Tests
# --------------------------
def test_hugging_face_provider_init():
    ai_provider = HuggingFaceProvider()
    assert ai_provider.api_key is not None
    assert ai_provider.device is not None
    assert ai_provider.model_name is not None
    assert ai_provider.pipe is not None


def test_hugging_face_simple_response():
    ai_provider = HuggingFaceProvider()

    ai_provider._override_base_prompt("The capital of Brazil is ...")
    response = ai_provider.generate()

    _log(response, level="DEBUG")

    assert response is not None
    assert response["response"] is not None
    assert response["response"] != ""
    assert ("brasília" in response["response"].lower()) or (
        "brasilia" in response["response"].lower()
    )


# --------------------------
# GeminiProvider Tests
# --------------------------
def test_gemini_provider_init():
    ai_provider = GeminiProvider()
    assert ai_provider.api_key is not None
    assert ai_provider.model_name is not None


@pytest.mark.skip(
    reason="We can skip this as it will be tested in the test_gemini_generate_itinerary"
)
def test_gemini_simple_response():
    ai_provider = GeminiProvider()

    ai_provider._override_base_prompt("1+1 = ?")
    response = ai_provider.generate()

    _log(response, level="DEBUG")

    assert response is not None
    assert response["response"] is not None
    assert response["response"] != ""
    assert "2" in response["response"]


def test_gemini_generate_itinerary():
    ai_provider = GeminiProvider()
    itinerary_request = mock_itinerary_gen_request()

    ai_provider.prepare(**itinerary_request)
    response = ai_provider.generate()

    # Test the response
    _log(response, level="DEBUG")

    assert response is not None
    assert response["response"] is not None
    assert response["response"] != ""

    # Test the itinerary conversion
    itinerary = ai_provider._to_itinerary(response)
    _log(itinerary, level="DEBUG")
