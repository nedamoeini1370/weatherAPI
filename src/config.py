from os import environ

API_URL = "https://www.7timer.info/bin/astro.php"
OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json"
DATE_FORMAT = "%Y%m%d%H"
OPENCAGE_API_KEY = environ.get("OPENCAGE_API_KEY")  # Get the API key from the environment
