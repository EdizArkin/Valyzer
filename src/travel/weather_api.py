import requests
from src.config import OPENWEATHERMAP_API_KEY

class WeatherAPI:
    def __init__(self, api_key = OPENWEATHERMAP_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city_name):
        try:
            response = requests.get(
                f"https://wttr.in/{city_name}?format=j1"
            )
            data = response.json()
            current = data["current_condition"][0]
            temp_c = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            icon_url = current["weatherIconUrl"][0]["value"]
            return {
                "city": city_name,
                "temp": temp_c,
                "desc": desc,
                "icon": icon_url
            }
        except:
            return None