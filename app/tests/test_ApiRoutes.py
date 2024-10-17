import json
import pytest
from unittest.mock import patch, mock_open
from routes.api import get_available_api_keys


# Test the get_available_api_keys function
def test_get_available_api_keys():

    # Mock the os.environ dictionary
    with patch.dict(
        "os.environ", {"FASTAPI_KEYS": "75575c0153f1b463a879187656e121c9:test"}
    ):
        keys = get_available_api_keys()
        # Assert the expected parsed dictionary result
        assert keys == {"75575c0153f1b463a879187656e121c9": "test"}
