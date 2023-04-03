**Weather API**


This is a simple weather API that provides weather information for a location based on latitude and longitude or postcode in Spain.


**Endpoints**

`GET /`

A GET request to obtain weather information for a location based on latitude and longitude.

**Parameters**

lat (float): Latitude of the location.

lon (float): Longitude of the location.

**Response**

Returns a list of dictionaries containing weather information for the location over the next 48 hours.


Each dictionary contains:

`start_period_utc (str)`: The start of the time point interval in unambiguous UTC timezone, with format "YYYYMMDDHH"

`end_period_utc (str)`: The end of the time point interval in unambiguous UTC timezone, with format "YYYYMMDDHH".

`cloud_cover (str)`: The percentage of cloud cover.

`temperature (str)`: The temperature at 2 meters above ground level in Celsius.

**Example**

`$ curl "http://localhost:8000/?lat=40.41&lon=-3.7"
[
    {
        "start_period_utc": "202204031200",
        "end_period_utc": "202204031500",
        "cloud_cover": "0",
        "temperature": "12",
    },
    {
        "start_period_utc": "202204031500",
        "end_period_utc": "202204031800",
        "cloud_cover": "0",
        "temperature": "11",
    },
    ...
]`

`GET /weather/code`

A GET request to obtain weather information for a location based on postcode in Spain.

**Parameters**

`postcode` (str): Postcode of the location in Spain.

**Response**

Returns a list of dictionaries containing weather information for the location over the next 48 hours.

Each dictionary contains:

Example

`$ curl "http://localhost:8000/weather/code?postcode=28013"
[
    {
        "start_period_utc": "202204031200",
        "end_period_utc": "202204031500",
        "cloud_cover": "0",
        "temperature": "12",
    },
    {
        "start_period_utc": "202204031500",
        "end_period_utc": "202204031800",
        "cloud_cover": "0",
        "temperature": "11",
    },
    ...
]`

**How to Run**

**Installation**

* Clone the repository
* Create a virtual environment: python3 -m venv env
* Activate the virtual environment: source env/bin/activate
* Install the dependencies: pip install -r requirements.txt
* Set the environment variable for OpenCage API key: export OPENCAGE_API_KEY=your_api_key
* Starting the API
* To start the API, run uvicorn main:app --reload in your terminal.

**Run by Docker**

`docker build -t weather-api .`

**Future Improvements**

* Add more weather parameters, such as solar radiation, wind speed and direction, precipitation, and pressure.
* Add caching mechanism to reduce the number of API calls.
* Add more tests.