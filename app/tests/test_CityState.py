import json
from unittest.mock import patch, mock_open
from services.CityState import CityStateData

from tests.mocks import mock_city_state_json_data


@patch("services.AppData")
@patch("builtins.open", new_callable=mock_open)
def test_init(mock_open, mock_get_config):
    # Mocking AppData to return a fake JSON file path
    mock_get_config.return_value = "fake_path.json"

    # Mock the file read to return the mock JSON data
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        mock_city_state_json_data()
    )

    city_state_data = CityStateData()

    assert city_state_data.city_state_data == mock_city_state_json_data()


def test_get_states():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    states = city_state_data.get_states()

    assert states == ["São Paulo", "Rio de Janeiro"]


def test_get_ufs():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    ufs = city_state_data.get_ufs()

    assert ufs == ["SP", "RJ"]


def test_get_cities_by_state():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    cities_sp = city_state_data.get_cities_by_state("São Paulo")
    cities_rj = city_state_data.get_cities_by_state("Rio de Janeiro")

    assert cities_sp == ["São Paulo", "Campinas", "Santos"]
    assert cities_rj == ["Rio de Janeiro", "Niterói", "Petropolis"]


def test_get_cities_by_state_not_found():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    cities = city_state_data.get_cities_by_state("Bahia")  # Non-existing state
    assert cities == []


def test_get_cities_by_uf():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    cities_sp = city_state_data.get_cities_by_uf("SP")
    cities_rj = city_state_data.get_cities_by_uf("RJ")

    assert cities_sp == ["São Paulo", "Campinas", "Santos"]
    assert cities_rj == ["Rio de Janeiro", "Niterói", "Petropolis"]


def test_get_cities_by_uf_not_found():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    cities = city_state_data.get_cities_by_uf("BA")  # Non-existing UF
    assert cities == []


def test_uf_to_state():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    state_sp = city_state_data.uf_to_state("SP")
    state_rj = city_state_data.uf_to_state("RJ")

    assert state_sp == "São Paulo"
    assert state_rj == "Rio de Janeiro"


def test_uf_to_state_not_found():
    city_state_data = CityStateData()
    city_state_data.city_state_data = mock_city_state_json_data()

    state = city_state_data.uf_to_state("BA")  # Non-existing UF
    assert state == ""
