import requests
import re
from datetime import datetime, timedelta
import pandas as pd
from src.config import AMADEUS_API_KEY, AMADEUS_API_SECRET

class travel_scraper:
    def __init__(self, api_key=AMADEUS_API_KEY, api_secret=AMADEUS_API_SECRET):
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = self.get_access_token()

    def get_access_token(self):
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def extract_iata(self, airport_str):
        match = re.search(r'\((\w{3})\)', airport_str)
        return match.group(1) if match else airport_str

    # Using the Amadeus API to fetch travel data information
    def fetch_travel_data(self, origin, destination, travel_date, days_window=0):
        base_date = datetime.strptime(travel_date, "%Y-%m-%d")

        # Date range for future machine learning model
        date_range = [base_date + timedelta(days=i) for i in range(-days_window, days_window + 1)]

        # Extract IATA codes from the origin and destination strings
        # Example: "Istanbul Airport (IST)" -> "IST"
        origin_code = self.extract_iata(origin)
        destination_code = self.extract_iata(destination)

        all_flights = []

        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")
            flights = self.search_flights_amadeus(origin_code, destination_code, date_str)

            for offer in flights.get("data", []):
                price = offer.get("price", {}).get("total")
                for itinerary in offer.get("itineraries", []):
                    segments = itinerary.get("segments", [])
                    if not segments:
                        continue

                    # segment[0] is the first flight segment (departure), segment[-1] is the last flight segment (arrival)
                    if segments[0]["departure"]["iataCode"] != origin_code or \
                    segments[-1]["arrival"]["iataCode"] != destination_code:
                        continue

                    route = " → ".join([seg["departure"]["iataCode"] for seg in segments] + [segments[-1]["arrival"]["iataCode"]])
                    carriers = ", ".join([seg["carrierCode"] for seg in segments])
                    flight_numbers = ", ".join([seg["carrierCode"] + seg["number"] for seg in segments])
                    departure_at = segments[0]["departure"]["at"]
                    arrival_at = segments[-1]["arrival"]["at"]

                    # Duration calculation
                    departure_time = datetime.fromisoformat(departure_at.replace("Z", "+00:00"))
                    arrival_time = datetime.fromisoformat(arrival_at.replace("Z", "+00:00"))
                    duration = arrival_time - departure_time
                    duration_str = str(duration).split(", ")[-1]


                    stops = len(segments) - 1
                    flight_type = "Direct" if stops == 0 else "Connecting"

                    all_flights.append({
                        "date": date_str,
                        "origin": origin_code,
                        "destination": destination_code,
                        "price": price,
                        "flight_type": flight_type,
                        "route": route,
                        "duration": duration_str,
                        "departure_time": departure_time.strftime("%H:%M"),
                        "arrival_time": arrival_time.strftime("%H:%M"),
                        #"departure_at": departure_at, # Uncomment if you want to include departureDate + departureTime in the output
                        #"arrival_at": arrival_at, # Uncomment if you want to include arrivalDate + arrivalTime in the output
                        "carriers": carriers,
                        "flight_numbers": flight_numbers,
                        #"stops": stops # Uncomment if you want to include transfer number in the output
                    })

        df = pd.DataFrame(all_flights)
        return df


    def search_flights_amadeus(self, origin_code, destination_code, date):
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": date,
            "adults": 1,
            "travelClass": "ECONOMY",
            "currencyCode": "TRY",
            "max": 10
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            self.token = self.get_access_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        return response.json()
