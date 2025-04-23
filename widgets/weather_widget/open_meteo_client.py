import numpy as np
import openmeteo_requests
from openmeteo_sdk.Variable import Variable

om = openmeteo_requests.Client()
params = {
    "latitude": 33.49,
    "longitude":-101.93,
    "hourly": ["temperature_2m","precipitation","wind_speed_10m"],
    "current":["temperature_2m","precipitation"],
    "timezone":"America/Chicago",
    "temperature_unit":"Fahrenheit",
    "windspeed_unit":"mph",
    "precipitation_unit":"inch"
}



