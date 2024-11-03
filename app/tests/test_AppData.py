import os
import json
import pytest
from unittest import mock

from services.AppData import AppData


@pytest.fixture
def app_data():
    return AppData()


def test_get_config_key_exists(app_data, tmpdir):
    # Create a temporary config file
    config_data = {"database_host": "localhost"}
    config_file = tmpdir.join("cfg.json")
    config_file.write(json.dumps(config_data))

    # Mock os.path.exists to simulate the config file path
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch(
            "builtins.open", mock.mock_open(read_data=json.dumps(config_data))
        ):
            result = app_data.get_config("database_host")
            assert result == "localhost"


def test_get_config_key_not_exists(app_data, tmpdir):
    config_data = {"database_host": "localhost"}

    # Mock os.path.exists and open
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch(
            "builtins.open", mock.mock_open(read_data=json.dumps(config_data))
        ):
            result = app_data.get_config("non_existent_key")
            assert result is None


def test_get_config_override(app_data, tmpdir):
    # Sample config data that would exist in the JSON file
    config_data = {"permanent_storage_dir": "./data/02_processed/"}
    config_file = tmpdir.join("cfg.json")
    config_file.write(json.dumps(config_data))

    # Mock the environment variable to test override functionality
    with mock.patch.dict(
        os.environ, {"__CONFIG_OVERRIDE_permanent_storage_dir": "__OVERRIDE__"}
    ):
        # Mock os.path.exists to simulate the config file path and open to read the mocked config data
        with mock.patch("os.path.exists", return_value=True):
            with mock.patch(
                "builtins.open", mock.mock_open(read_data=json.dumps(config_data))
            ):
                result = app_data.get_config("permanent_storage_dir")
                # Assert that the environment variable value takes precedence over the config file value
                assert result == "__OVERRIDE__"


def test_get_config_no_override(app_data, tmpdir):
    # Sample config data that would exist in the JSON file
    config_data = {"permanent_storage_dir": "./data/02_processed/"}
    config_file = tmpdir.join("cfg.json")
    config_file.write(json.dumps(config_data))

    # Ensure there's no environment variable for the key
    if "__CONFIG_OVERRIDE_permanent_storage_dir" in os.environ:
        del os.environ["__CONFIG_OVERRIDE_permanent_storage_dir"]

    # Mock os.path.exists to simulate the config file path and open to read the mocked config data
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch(
            "builtins.open", mock.mock_open(read_data=json.dumps(config_data))
        ):
            result = app_data.get_config("permanent_storage_dir")
            # Assert that the JSON file value is used when there's no environment override
            assert result == "./data/02_processed/"


def test_get_api_key_found(app_data):
    with mock.patch.dict(os.environ, {"GOOGLEMAPS_API_KEY": "test_api_key"}):
        result = app_data.get_api_key("googlemaps")
        assert result == "test_api_key"


def test_get_api_key_not_found(app_data):
    result = app_data.get_api_key("non_existent_key")
    assert result is None


def test_save_data_success(app_data, tmpdir):
    test_data = {"destination": "Paris", "duration": 7}
    type = "trip"
    id = "paris_2023"

    # Mock methods and paths
    save_path = tmpdir.join("trip")
    save_path.mkdir()

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        with mock.patch.object(app_data, "_save_file", return_value=True):
            result = app_data.save(type, id, test_data)
            assert result is True


def test_save_data_file_exists_no_replace(app_data, tmpdir):
    test_data = {"destination": "Paris", "duration": 7}
    type = "trip"
    id = "paris_2023"

    save_path = tmpdir.join("trip")
    save_path.mkdir()
    file_path = save_path.join(f"{id}.json")
    file_path.write(json.dumps(test_data))  # Simulate existing file

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        with mock.patch("os.path.exists", return_value=True):
            result = app_data.save(type, id, test_data, replace=False)
            assert result is False


def test_get_data_success(app_data, tmpdir):
    test_data = {"destination": "Paris", "duration": 7}
    type = "trip"
    id = "paris_2023"

    save_path = tmpdir.join("trip")
    save_path.mkdir()
    file_path = save_path.join(f"{id}.json")
    file_path.write(json.dumps(test_data))

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        result = app_data.get(type, id)
        assert result == test_data


def test_get_data_not_found(app_data, tmpdir):
    type = "trip"
    id = "non_existent_id"

    save_path = tmpdir.join("trip")
    save_path.mkdir()

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        result = app_data.get(type, id)
        assert result is None


def test_get_data_invalid_json(app_data, tmpdir):
    type = "trip"
    id = "invalid_json"

    save_path = tmpdir.join("trip")
    save_path.mkdir()
    file_path = save_path.join(f"{id}.json")
    file_path.write("invalid_json")

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        result = app_data.get(type, id)
        assert result is None


def test_update_data_success(app_data, tmpdir):
    original_data = {"destination": "Paris", "duration": 7}
    updated_value = "10"
    type = "trip"
    id = "paris_2023"

    save_path = tmpdir.join("trip")
    save_path.mkdir()
    file_path = save_path.join(f"{id}.json")
    file_path.write(json.dumps(original_data))

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        with mock.patch.object(app_data, "save", return_value=True):
            result = app_data.update(type, id, "duration", updated_value)
            assert result is True


def test_delete_data_success(app_data, tmpdir):
    type = "trip"
    id = "paris_2023"

    save_path = tmpdir.join("trip")
    save_path.mkdir()
    file_path = save_path.join(f"{id}.json")
    file_path.write(json.dumps({"destination": "Paris", "duration": 7}))

    with mock.patch.object(
        app_data, "_get_storage_map", return_value={type: str(save_path)}
    ):
        with mock.patch.object(app_data, "_delete_file", return_value=True):
            result = app_data.delete(type, id)
            assert result is True


def test_sanitize_id_success(app_data):
    raw_id = "My Trip 2023!"
    sanitized_id = app_data.sanitize_id(raw_id)
    assert sanitized_id == "my_trip_2023"


def test_sanitize_id_invalid(app_data):
    with pytest.raises(ValueError):
        app_data.sanitize_id("")
