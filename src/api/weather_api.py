import requests
from src.config.config import OPENWEATHERMAP_API_KEY

class WeatherAPI:
    def __init__(self, api_key = OPENWEATHERMAP_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city_name):
        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={self.api_key}"
            )
            data = response.json()

            current = data["main"]
            weather_info = data["weather"][0]

            temp_c = current["temp"] - 273.15
            feels_like_c = current["feels_like"] - 273.15
            max_temp_c = current["temp_max"] - 273.15
            min_temp_c = current["temp_min"] - 273.15
            desc = weather_info["description"].strip().lower()
            icon_code = weather_info["icon"]

            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            return {
                "city": data.get("name", city_name),
                "temp": round(temp_c, 1),
                "feels_like": round(feels_like_c, 1),
                "desc": desc.title(),
                "icon": icon_url,
                "max_temp": round(max_temp_c, 1),
                "min_temp": round(min_temp_c, 1)
            }

        except Exception as e:
            print(f"Weather fetch error: {e}")
            return None

