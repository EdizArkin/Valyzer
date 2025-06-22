from src.services.DataManager import DataManager
from src.travel.travel_scraper import fetch_travel_data


class TravelService:
    def __init__(self):
        self.repo = DataManager()

    def get_airports(self):
        """
        Loads and returns a list of airports.
        """
        return self.repo.load_airports()
    
    def get_travel_data(self, origin, destination, travel_date, days_window = 7):
        """
        Fetches travel data for the specified origin, destination, and travel date.
        Returns a DataFrame with flight prices and details.
        """
        return fetch_travel_data(origin, destination, travel_date, days_window)

# İleri işlemler: fiyat tahmini, filtre vs