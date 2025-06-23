from unittest import result
from src.services.DataManager import DataManager
from src.travel.travel_scraper import travel_scraper


class TravelService:
    def __init__(self):
        self.repo = DataManager()
        self.scraper = travel_scraper()

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

    
# Future work: price prediction, filter etc.