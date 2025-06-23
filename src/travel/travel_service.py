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
    
    def get_travel_data(self, origin, destination, travel_date, classInfo, numOfAdults, days_window=7):
        """
        Fetches travel data for the specified origin, destination, and travel date.
        Returns a DataFrame with flight prices and details.
        """
        return self.scraper.fetch_travel_data(origin, destination, travel_date, classInfo, numOfAdults, days_window)

# Future work: price prediction, filter etc.