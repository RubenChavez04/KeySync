from datetime import datetime, timedelta
import openmeteo_requests
import pytz
import requests_cache
import pandas as pd
from retry_requests import retry

import geocoder
def get_coordinates():
    # Get location based on your public IP
    g = geocoder.ip('me')
    return g.latlng  # Returns [latitude, longitude]

class OpenMeteoClient:
    def __init__(self):
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=self.retry_session)
        coords = get_coordinates()
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": coords[0],
            "longitude": coords[1],
            "daily": ["precipitation_probability_max", "temperature_2m_min", "temperature_2m_max","sunrise", "sunset"],
            "hourly": ["temperature_2m", "precipitation_probability", "wind_speed_10m", "weather_code"],
            "current": ["wind_speed_10m", "temperature_2m", "weather_code", "is_day"],
            "timezone": "America/Chicago",
            "forecast_days": 1,
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "models": "gfs_seamless"
        }

        self.response = self.client.weather_api(self.url, params=self.params)[0]

    def get_current(self):
        print("getting current")
        current = self.response.Current()
        time = datetime.utcfromtimestamp(current.Time()).replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("America/Chicago"))
        return {
            "time": time.strftime("%m/%d %I:%M %p"),
            "wind_speed_10m": round(current.Variables(0).Value()),
            "temperature_2m": round(current.Variables(1).Value()),
            "weather_code": round(current.Variables(2).Value()),
            "is_day":int(current.Variables(3).Value())
        }

    def get_hourly(self):
        hourly = self.response.Hourly()
        temperature_2m = hourly.Variables(0).ValuesAsNumpy().round(0).astype(int)
        precipitation_probability = hourly.Variables(1).ValuesAsNumpy().round(0).astype(int)
        wind_speed_10m = hourly.Variables(2).ValuesAsNumpy().round(0).astype(int)
        weather_codes = hourly.Variables(3).ValuesAsNumpy().astype(int)

        dates = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ).tz_convert("America/Chicago").strftime("%I%p")

        dates = [date.lstrip("0") for date in dates]

        return pd.DataFrame({
            "date": dates,
            "temperature_2m": temperature_2m,
            "precipitation_probability": precipitation_probability,
            "wind_speed_10m": wind_speed_10m,
            "weather_codes": weather_codes
        })

    def get_daily(self):
        daily = self.response.Daily()
        temperature_min = daily.Variables(1).ValuesAsNumpy().round(0).astype(int)
        temperature_max = daily.Variables(2).ValuesAsNumpy().round(0).astype(int)
        precipitation_max = daily.Variables(0).ValuesAsNumpy().round(0).astype(int)
        sunrise = daily.Variables(3).ValuesInt64AsNumpy()
        sunset = daily.Variables(4).ValuesInt64AsNumpy()
        sunrise_times = [datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("America/Chicago")).strftime("%I:%M %p") for ts in sunrise]
        sunset_times = [datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("America/Chicago")).strftime("%I:%M %p") for ts in sunset]

        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ).tz_convert("America/Chicago").strftime("%m/%d %I:%M %p")

        return pd.DataFrame({
            "date": dates,
            "temperature_2m_min": temperature_min,
            "temperature_2m_max": temperature_max,
            "precipitation_probability_max": precipitation_max,
            "sunrise": sunrise_times,
            "sunset": sunset_times
        })


