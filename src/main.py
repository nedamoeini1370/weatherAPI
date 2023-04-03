from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import FastAPI, Query, HTTPException
import httpx

from src.config import API_URL, DATE_FORMAT, OPENCAGE_URL, OPENCAGE_API_KEY
from pydantic import BaseModel

app = FastAPI()


class WeatherData(BaseModel):
    start_period_utc: str
    end_period_utc: str
    cloud_cover: str
    temperature: str

    @classmethod
    async def from_api_data(cls, data: dict) -> list["WeatherData"]:
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
            result.append(cls(**weather_data))

        return result


async def get_weather_data(lat: float, lon: float) -> dict:
    params = {
        "lat": f"{lat:.2f}",
        "lon": f"{lon:.2f}",
        "unit": "metric",
        "output": "json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL, params=params)
        response.raise_for_status()
    return response.json()


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

    data = await get_weather_data(lat, lon)
    return await WeatherData.from_api_data(data)


async def get_lat_lon(postcode: str) -> Optional[tuple]:
    url = f"{OPENCAGE_URL}?q={postcode},Spain&key=" \
                   f"{OPENCAGE_API_KEY}&language=en&pretty=1&limit=1&no_annotations=1"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        if data["total_results"] == 0:
            return None
        else:
            lat = data["results"][0]["geometry"]["lat"]
            lon = data["results"][0]["geometry"]["lng"]
            return lat, lon


@app.get("/weather/code", response_model=list[WeatherData])
async def get_weather_by_postcode(postcode: str) -> list[WeatherData]:
    lat_lon = await get_lat_lon(postcode)
    if lat_lon is None:
        raise HTTPException(status_code=422, detail="Invalid postcode")
    else:
        lat, lon = lat_lon
        data = await get_weather_data(lat, lon)
        return await WeatherData.from_api_data(data)
