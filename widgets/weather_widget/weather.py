from widgets.weather_widget.open_meteo_client import OpenMeteoClient
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

weather = OpenMeteoClient()

current = weather.get_current()
print("-" * 20 + "Current" + "-" * 20)
for key, val in current.items():
    print(f"{key}: {val}")

print("-" * 20 + "Hourly" + "-" * 20)
print(weather.get_hourly())

print("-" * 20 + "Daily" + "-" * 20)
print(weather.get_daily())

print("-" * 20 + "12 Hours" + "-" * 20)
print(weather.get_hourly_next_12_hours())