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

    def get_hotels_by_city(self, destination):
        """
        Fetches hotels in the specified city using its IATA code.
        Returns a DataFrame with hotel details.
        """
        result = self.scraper.fetch_hotels_by_city(destination)

        # If an error is returned, return it directly to 2_Travel.py
        if isinstance(result, dict) and "error" in result:
            return result
        
        return result


# Future work: price prediction, filter etc.