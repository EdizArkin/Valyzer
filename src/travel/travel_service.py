from src.services.DataManager import DataManager


class TravelService:
    def __init__(self):
        self.repo = DataManager()

    def get_airports(self):
        """
        Loads and returns a list of airports.
        """
        return self.repo.load_airports()


# İleri işlemler: fiyat tahmini, filtre vs