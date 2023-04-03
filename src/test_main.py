from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.config import DATE_FORMAT
from src.main import app

client = TestClient(app)


# Define a function to mock the 7timer API request
async def mocked_get_7timer(*args, **kwargs):
    # Define a mocked response from the 7timer API
    mock_response = {
        "init": "2022040512",
        "dataseries": [
            {"timepoint": 0, "cloudcover": 0, "temp2m": 20},
            {"timepoint": 3, "cloudcover": 10, "temp2m": 18},
            {"timepoint": 6, "cloudcover": 30, "temp2m": 16},
            {"timepoint": 9, "cloudcover": 50, "temp2m": 14},
        ],
    }
    response = MagicMock()
    response.json = MagicMock(return_value=mock_response)
    return response


# Define a function to test the get_weather endpoint
@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new=mocked_get_7timer)
async def test_get_weather():
    lat, lon = 40.4168, -3.7038
    response = client.get(f"/?lat={lat}&lon={lon}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    mock_response = await mocked_get_7timer()
    mock_response = mock_response.json.return_value
    start_time = datetime.strptime(mock_response["init"], "%Y%m%d%H")
    for i, item in enumerate(mock_response["dataseries"]):
        end_period_utc = start_time + timedelta(hours=item["timepoint"])
        start_period_utc = end_period_utc - timedelta(hours=3)
        assert data[i]["start_period_utc"] == start_period_utc.strftime(DATE_FORMAT)
        assert data[i]["end_period_utc"] == end_period_utc.strftime(DATE_FORMAT)
        assert data[i]["cloud_cover"] == str(item["cloudcover"])
        assert data[i]["temperature"] == str(item["temp2m"])


def test_get_weather_invalid_lat():
    lat, lon = 91, -0.1276
    response = client.get(f"/?lat={lat}&lon={lon}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "ensure this value is less than 90"


def test_get_weather_invalid_lon():
    lat, lon = 51.5072, -181
    response = client.get(f"/?lat={lat}&lon={lon}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "ensure this value is greater than -180"


def test_get_weather_invalid_input():
    lat, lon = "invalid_lat", "invalid_lon"
    response = client.get(f"/?lat={lat}&lon={lon}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid float"
