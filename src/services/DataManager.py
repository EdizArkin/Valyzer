import csv

class DataManager:
    def __init__(self, data_folder="data/RawDatasets"):
        self.data_folder = data_folder
        self.airports = []

    def load_airports(self, filename="airports.csv"):
        path = f"{self.data_folder}/{filename}"
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name = row[1].strip()
                city = row[2].strip()
                iata = row[4].strip()

                if iata and len(iata) == 3:
                    if city:
                        display_name = f"{city} - {name} ({iata})"
                    else:
                        display_name = f"{name} ({iata})"
                    self.airports.append(display_name)

        self.airports.sort()
        return self.airports


    # for future use, if needed:
    # def get_flight_prices(...)
    # def query_database(...)
