from lib.Utils import Utils

import pytest

from services.AiProvider import AiProvider
from services.Logger import _log
from services.HuggingFaceProvider import HuggingFaceProvider
from services.GeminiProvider import GeminiProvider
from services.SentimentAnalysisProvider import SentimentAnalyzer

from tests.test_Trip import mock_trip_model, mock_trip
from tests.test_Itinerary import mock_activity, mock_itinerary
from tests.test_Attractions import mock_attractions

from models.Itinerary import DailyItineraryModel


def mock_weather():
    return mock_trip_model().weather


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


# --------------------------
# AiProvider Tests
# --------------------------
def test_generate_weather_summary():
    ai_provider = AiProvider()

    itinerary_request = mock_ai_gen_itinerary_request()
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
    itinerary_request = mock_ai_gen_itinerary_request()
    forecast_list = None

    summary = ai_provider._generate_weather_summary(
        forecast_list=forecast_list,
        start_date=itinerary_request["start_date"],
        end_date=itinerary_request["end_date"],
    )

    test_summary = "* Não há dados do tempo disponíveis"

    assert test_summary in summary


def test_generate_goals_summary():
    ai_provider = AiProvider()
    goals = mock_trip_model().goals
    ai_provider.prepare(goals=goals)
    summary = ai_provider._generate_prompt_from_template(
        template_key="gen_itinerary_prompt"
    )

    test_summary = "* " + goals.replace("\n", "\n* ").replace("  ", " ")

    _log(summary, level="DEBUG")

    assert test_summary in summary


def test_generate_attractions_summary():
    ai_provider = AiProvider()
    attractions_list = mock_ai_gen_itinerary_request()["attractions_list"]

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


def test_generate_itinerary_summary():
    ai_provider = AiProvider()
    itinerary = mock_itinerary()

    summary = ai_provider._generate_itinerary_summary(itinerary=itinerary)
    _log(summary, level="DEBUG")

    # Check for the presence of the test strings
    test_summary = f"### {Utils.to_date_string(itinerary[0].date, format='display')} - {itinerary[0].title} \n"
    assert test_summary in summary

    activity = itinerary[0].items[0]
    test_summary = f"* [{Utils.to_time_string(activity.start_time)} - {Utils.to_time_string(activity.end_time)}] {activity.title} | {activity.location}"

    assert test_summary in summary


def test_full_trip_template_replace():
    ai_provider = AiProvider()
    trip_model = mock_trip_model()

    test_prompt = "%%TRIP_JSON%%"
    ai_provider.prepare(trip_model=trip_model)

    final_prompt = ai_provider._generate_prompt_from_template(base_prompt=test_prompt)
    _log(final_prompt, level="DEBUG")

    assert "destination_city" in final_prompt
    assert "destination_state" in final_prompt
    assert "start_date" in final_prompt
    assert "end_date" in final_prompt


def test_generate_final_prompt():
    ai_provider = AiProvider()
    itinerary_request = mock_ai_gen_itinerary_request()

    ai_provider.prepare(**itinerary_request)

    prompt = ai_provider._generate_prompt_from_template()

    # Check for the presence of the test strings

    # Location
    assert itinerary_request["location"] in prompt

    # Weather summary
    forecast_item = itinerary_request["forecast_list"][0]
    date = Utils.to_date_string(forecast_item.date, format="iso_date_only")
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
    response = mock_ai_gen_itinerary_response()

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

    response = ai_provider.prompt(prompt="The capital of Brazil is ...")

    _log(response, level="DEBUG")

    assert response is not None
    assert response != ""
    assert ("brasília" in response.lower()) or ("brasilia" in response.lower())


def test_hugging_face_summarize_sentence():
    ai_provider = HuggingFaceProvider()

    prompt = """
    Summarize this text:
    
    Think of it as a simple matter of supply and demand. Although the labor market has eased from the days of COVID-19, it remains tight, and unemployment is currently 4.1%. Businesses still report difficulty finding workers.
    Meanwhile, in some sectors of the economy – construction, hospitality and agriculture – foreign-born workers make up a significant percentage of the labor pool. And many of them are immigrants in the country illegally or workers who may have temporary visas.
    """
    response = ai_provider.prompt(prompt=prompt)

    _log(response, level="DEBUG")

    assert response is not None
    assert response != ""


@pytest.mark.skip(reason="This won't work yet")
def test_hugging_face_generate_trip_summary():
    ai_provider = HuggingFaceProvider()
    trip_model = mock_trip_model()

    ai_provider.prepare(trip_model=trip_model)
    trip_summary = ai_provider.generate_trip_summary()

    _log(trip_summary, level="DEBUG")

    assert trip_summary is not None
    assert trip_summary != ""


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

    response = ai_provider.prompt("1+1 = ?")

    _log(response, level="DEBUG")

    assert response is not None
    assert response != ""
    assert "2" in response


def test_gemini_generate_itinerary():
    ai_provider = GeminiProvider()
    itinerary_request = mock_ai_gen_itinerary_request()

    ai_provider.prepare(**itinerary_request)
    response = ai_provider.generate_itinerary()

    # Test the response
    _log(response, level="DEBUG")

    assert response is not None
    assert response != ""
    assert type(response[0]) == DailyItineraryModel


def test_gemini_generate_trip_summary():
    ai_provider = GeminiProvider()
    trip_model = mock_trip_model()

    ai_provider.prepare(trip_model=trip_model)
    trip_summary = ai_provider.generate_trip_summary()

    _log(trip_summary, level="DEBUG")

    assert trip_summary is not None
    assert trip_summary != ""


# --------------------------
# Sentiment Analysis Tests
# --------------------------
# Test initialization
def test_sentiment_analysis_init():
    ai_provider = SentimentAnalyzer()
    assert ai_provider.model_name is not None


# Test the ask method with a "negative" prompt
def test_sentiment_analysis_negative():
    ai_provider = SentimentAnalyzer()
    sentiment = ai_provider.analyze_sentiment("I hate this movie, it's terrible!")
    assert sentiment is not None
    assert sentiment != ""
    assert "NEGATIVE" in sentiment
