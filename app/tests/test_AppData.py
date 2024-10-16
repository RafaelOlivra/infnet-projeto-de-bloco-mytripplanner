import pytest
import os
import json
from unittest.mock import patch, mock_open
from services.AppData import AppData


class TestAppData:
    @pytest.fixture
    def app_data(self):
        return AppData()

    @pytest.fixture
    def mock_config(self):
        return {
            "temp_storage_dir": "/tmp/app_data",
            "permanent_storage_dir": "/var/app_data",
        }

    @patch("os.path.exists")
    @patch(
        "builtins.open", new_callable=mock_open, read_data='{"test_key": "test_value"}'
    )
    def test_get_config(self, mock_file, mock_exists, app_data):
        mock_exists.return_value = True
        assert app_data.get_config("test_key") == "test_value"

    @patch.dict(os.environ, {"GOOGLEMAPS_API_KEY": "test_api_key"})
    def test_get_api_key(self, app_data):
        assert app_data.get_api_key("googlemaps") == "test_api_key"

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app_data.AppData._get_storage_map")
    def test_save(self, mock_storage_map, mock_file, mock_exists, app_data):
        mock_storage_map.return_value = {"trip": "/tmp/app_data/trip"}
        mock_exists.return_value = False
        assert app_data.save("trip", "test_trip", {"destination": "Paris"})

    @patch("os.path.exists")
    @patch(
        "builtins.open", new_callable=mock_open, read_data='{"destination": "Paris"}'
    )
    @patch("app_data.AppData._get_storage_map")
    def test_get(self, mock_storage_map, mock_file, mock_exists, app_data):
        mock_storage_map.return_value = {"trip": "/tmp/app_data/trip"}
        mock_exists.return_value = True
        assert app_data.get("trip", "test_trip") == {"destination": "Paris"}

    @patch("os.listdir")
    @patch("app_data.AppData._get_storage_map")
    @patch("app_data.AppData.get")
    def test_get_all(self, mock_get, mock_storage_map, mock_listdir, app_data):
        mock_storage_map.return_value = {"trip": "/tmp/app_data/trip"}
        mock_listdir.return_value = ["trip1.json", "trip2.json"]
        mock_get.side_effect = [{"id": "trip1"}, {"id": "trip2"}]
        assert app_data.get_all("trip") == [{"id": "trip1"}, {"id": "trip2"}]

    @patch("os.listdir")
    @patch("app_data.AppData._get_storage_map")
    def test_get_all_ids(self, mock_storage_map, mock_listdir, app_data):
        mock_storage_map.return_value = {"trip": "/tmp/app_data/trip"}
        mock_listdir.return_value = ["trip1.json", "trip2.json"]
        assert app_data.get_all_ids("trip") == ["trip1", "trip2"]

    @patch("app_data.AppData.get")
    @patch("app_data.AppData.save")
    def test_update(self, mock_save, mock_get, app_data):
        mock_get.return_value = {"destination": "Paris"}
        mock_save.return_value = True
        assert app_data.update("trip", "test_trip", "duration", "7")
        mock_save.assert_called_with(
            "trip", "test_trip", {"destination": "Paris", "duration": "7"}, replace=True
        )

    @patch("os.path.exists")
    @patch("os.remove")
    @patch("app_data.AppData._get_storage_map")
    def test_delete(self, mock_storage_map, mock_remove, mock_exists, app_data):
        mock_storage_map.return_value = {"trip": "/tmp/app_data/trip"}
        mock_exists.return_value = True
        assert app_data.delete("trip", "test_trip")
        mock_remove.assert_called_once()

    def test_sanitize_id(self, app_data):
        assert app_data.sanitize_id("Test Trip 2023!") == "test_trip_2023"
        with pytest.raises(ValueError):
            app_data.sanitize_id("a" * 51)  # Too long
        with pytest.raises(ValueError):
            app_data.sanitize_id("a" * 4)  # Too short
