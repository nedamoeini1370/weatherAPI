from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, Query
import httpx

from src.config import API_URL, DATE_FORMAT
from pydantic import BaseModel

app = FastAPI()


class WeatherData(BaseModel):
    start_period_utc: str
    end_period_utc: str
    cloud_cover: str
    temperature: str


@app.get("/", response_model=list[WeatherData])
async def get_weather(lat: Annotated[float, Query(lt=90, gt=-90)],
                      lon: Annotated[float, Query(lt=180, gt=-180)]
                      ) -> list[WeatherData]:
    """
    A GET request to obtain weather information for a location based on latitude and longitude.

    Parameters:
    - lat (float): Latitude of the location.
    - lon (float): Longitude of the location.

    Returns:
    - result (List[Dict[str, str]]): A list of dictionaries containing weather information for the location over the
    next 48 hours.

    Each dictionary contains:
    - start_period_utc (str): The start of the time point interval in unambiguous UTC timezone, with format "YYYYMMDDHH"
    - end_period_utc (str): The end of the time point interval in unambiguous UTC timezone, with format "YYYYMMDDHH".
    - cloudcover (str): The percentage of cloud cover.
    - temp2m (str): The temperature at 2 meters above ground level in Celsius.
    """
    params = {
        "lat": f"{lat:.2f}",
        "lon": f"{lon:.2f}",
        "unit": "metric",
        "output": "json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL, params=params)

    data = await response.json()
    start_time = datetime.strptime(data["init"], DATE_FORMAT).replace(tzinfo=timezone.utc)
    result = []

    for item in data["dataseries"]:
        end_period_utc = start_time + timedelta(hours=item["timepoint"])
        start_period_utc = end_period_utc - timedelta(hours=3)
        weather_data = {
            "start_period_utc": start_period_utc.strftime(DATE_FORMAT),
            "end_period_utc": end_period_utc.strftime(DATE_FORMAT),
            "cloud_cover": item["cloudcover"],
            "temperature": item["temp2m"],
        }
        result.append(WeatherData(**weather_data))

    return result
