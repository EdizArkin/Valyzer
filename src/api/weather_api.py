import requests
from src.config.config import OPENWEATHERMAP_API_KEY

class WeatherAPI:
    def __init__(self, api_key = OPENWEATHERMAP_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city_name):
        try:
            response = requests.get(f"https://wttr.in/{city_name}?format=j1")
            data = response.json()
            current = data["current_condition"][0]
            temp_c = current["temp_C"]
            desc = current["weatherDesc"][0]["value"].strip().lower()

            # OpenWeather desc-to-icon mapping
            desc_to_icon = {
                "sunny": "01d",
                "clear": "01d",
                "partly cloudy": "02d",
                "cloudy": "03d",
                "overcast": "04d",
                "mist": "50d",
                "patchy rain possible": "09d",
                "light rain": "10d",
                "moderate rain": "10d",
                "thunderstorm": "11d",
                "snow": "13d",
                "fog": "50d"
            }

            icon_code = desc_to_icon.get(desc, "01d")  # Default to sunny
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            return {
                "city": city_name,
                "temp": temp_c,
                "desc": desc.title(),
                "icon": icon_url
            }

        except Exception as e:
            print(f"Weather fetch error: {e}")
            return None
