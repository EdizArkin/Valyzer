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


    # Function to get access token from Amadeus API
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


    # Function to fetch travel data for a given origin, destination, and travel date
    def fetch_travel_data(self, origin, destination, travel_date, days_window=7):
        base_date = datetime.strptime(travel_date, "%Y-%m-%d")
        date_range = [base_date + timedelta(days=i) for i in range(-days_window, days_window + 1)]

        origin_code = self.extract_iata(origin)
        destination_code = self.extract_iata(destination)

        all_flights = []

        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")
            flights = self.search_flights_amadeus(origin_code, destination_code, date_str)
            for offer in flights.get("data", []):
                price = offer.get("price", {}).get("total")
                for itinerary in offer.get("itineraries", []):
                    for segment in itinerary.get("segments", []):
                        all_flights.append({
                            "date": date_str,
                            "price": price,
                            "origin": segment.get("departure", {}).get("iataCode"),
                            "destination": segment.get("arrival", {}).get("iataCode"),
                            "departure_at": segment.get("departure", {}).get("at"),
                            "arrival_at": segment.get("arrival", {}).get("at"),
                            "carrier_code": segment.get("carrierCode"),
                            "flight_number": segment.get("number")
                        })

        df = pd.DataFrame(all_flights)
        return df

    # Function to search flights using Amadeus API
    # This function handles the API request and token refresh if needed
    def search_flights_amadeus(self, origin, destination, date):
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1,
            "travelClass": "ECONOMY",
            "currencyCode": "TRY",
            "max": 10
        }
        response = requests.get(url, headers=headers, params=params)
        #----------------------------
        # Debugging output
        #print(response.status_code)
        #print(response.text)

        if response.status_code == 401:
            self.token = self.get_access_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
