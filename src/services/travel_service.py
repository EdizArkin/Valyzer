from src.services.DataManager import DataManager
from src.api.travel_scraper import travel_scraper
from src.api.weather_api import WeatherAPI


class TravelService:
    def __init__(self):
        self.repo = DataManager()
        self.scraper = travel_scraper()
        self.weather_api = WeatherAPI()

    def get_airports(self):
        """
        Loads and returns a list of airports.
        """
        return self.repo.load_airports()

    def get_travel_data(self, origin, destination, travel_date, classInfo, numOfAdults, selected_currency, days_window=7):
        """
        Fetches travel data for the specified origin, destination, and travel date.
        Returns a DataFrame with flight prices and details.
        """
        result = self.scraper.fetch_travel_data(origin, destination, travel_date, classInfo, numOfAdults, selected_currency, days_window)

        # If an error is returned, return it directly to 2_Travel.py
        if isinstance(result, dict) and "error" in result:
            return result

        return result
    
    def get_weather(self, city_name):
        """
        Fetches weather data for the specified city.
        Returns a dictionary with weather details.
        """
        result = self.weather_api.get_weather(city_name)

        # If an error is returned, return it directly to 2_Travel.py
        if result is None:
            return {"error": "Weather data not available", "status_code": 404}

        return result
    

    def get_destination_activities(self, destination):
        """
        Fetches activities for the specified destination.
        Returns a list of activities.
        """

        result = self.scraper.fetch_destination_activities(destination)

        # If an error is returned, return it directly to 2_Travel.py
        if isinstance(result, dict) and "error" in result:
            return result
        
        return result


    def extract_city_name(self, city_str):
        """
        Extracts city name from strings like 'Baruun Urt Airport (UUN)' or 'London, United Kingdom'.
        Removes airport codes and trims whitespace or generic suffixes like 'Airport'.
        """
        # 1. Remove text in parentheses (e.g., "(UUN)")
        if "(" in city_str:
            city_str = city_str.split("(")[0].strip()
            #print(f"Debug: After removing parentheses, city_str = '{city_str}'")  # Debugging

        # 2. Remove "Airport" suffix if present
        if "Airport" in city_str:
            city_str = city_str.replace("Airport", "").strip()
            #print(f"Debug: After removing 'Airport', city_str = '{city_str}'")  # Debugging

        # 3. Remove any trailing text after a hyphen (e.g., "Baruun Urt - Airport")
        if "-" in city_str:
            city_str = city_str.split("-")[0].strip()
            #print(f"Debug: After splitting by hyphen, city_str = '{city_str}'")  # Debugging


        # 4. If still has comma (like 'London, United Kingdom'), take the first part
        if "," in city_str:
            city_str = city_str.split(",")[0].strip()
            #print(f"Debug: After splitting by comma, city_str = '{city_str}'")  # Debugging

        return city_str

# Future work: price prediction, filter etc.