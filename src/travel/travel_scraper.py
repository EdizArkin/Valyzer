import requests
import re
from datetime import date, datetime, timedelta
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
    def fetch_travel_data(self, origin, destination, travel_date, classInfo, numOfAdults, selected_currency, days_window=7):
        base_date = datetime.strptime(travel_date, "%Y-%m-%d")

        # Date range for future machine learning model
        today = datetime.today()

        delta_days = (base_date - today).days

        # if the base_date is 7 days from today, give 14 days interval in the future
        if delta_days < 7:
            date_range = [base_date + timedelta(days=i) for i in range(0, 2 * days_window + 1)]
        # if the base_date is 7 days from today, give 14 days interval in the future
        else:
            date_range = [base_date + timedelta(days=i) for i in range(-days_window, days_window + 1)]


        # Extract IATA codes from the origin and destination strings
        # Example: "Istanbul Airport (IST)" -> "IST"
        origin_code = self.extract_iata(origin)
        destination_code = self.extract_iata(destination)

        all_flights = []

        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")
            flights = self.search_flights_amadeus(origin_code, destination_code, date_str, classInfo, numOfAdults)

            if isinstance(flights, dict) and "error" in flights:
                return {"error": flights["error"], "status_code": flights["status_code"]}

            for offer in flights.get("data", []):
                price = offer.get("price", {}).get("total")
                for itinerary in offer.get("itineraries", []):
                    segments = itinerary.get("segments", [])
                    if not segments:
                        continue

                    # segment[0] is the first flight segment (departure), segment[-1] is the last flight segment (arrival)
                    if segments[0]["departure"]["iataCode"] != origin_code or segments[-1]["arrival"]["iataCode"] != destination_code:
                        continue

                    route = " → ".join([seg["departure"]["iataCode"] for seg in segments] + [segments[-1]["arrival"]["iataCode"]])
                    carriers = ", ".join([seg["carrierCode"] for seg in segments])
                    flight_numbers = ", ".join([seg["carrierCode"] + seg["number"] for seg in segments])
                    departure_at = segments[0]["departure"]["at"]
                    arrival_at = segments[-1]["arrival"]["at"]

                    # Duration calculation
                    departure_time = datetime.fromisoformat(departure_at.replace("Z", "+00:00"))
                    arrival_time = datetime.fromisoformat(arrival_at.replace("Z", "+00:00"))
                    duration_str = str(arrival_time - departure_time).split(", ")[-1]

                    stops = len(segments) - 1
                    flight_type = "Direct" if stops == 0 else "Connecting"

                    try:
                        # Convert price if currency is different
                        if selected_currency != "EUR":
                            converted_price = convert_currency(float(price), 'EUR', selected_currency)
                            formatted_price = f"{converted_price:.2f} {selected_currency}"
                        else:
                            formatted_price = f"{float(price):.2f} EUR"

                        # Append adult info
                        if numOfAdults > 1:
                            price_str = f"{formatted_price} - for [{numOfAdults} Adults]"
                        else:
                            price_str = formatted_price
                    except Exception as e:
                        print(f"Currency conversion error: {e}")
                        price_str = f"{price} EUR (conversion failed)"

                    all_flights.append({
                        "date": date_str,
                        "origin": origin_code,
                        "destination": destination_code,
                        "price": price_str,
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

        return pd.DataFrame(all_flights)



    def search_flights_amadeus(self, origin_code, destination_code, date, classInfo="ECONOMY", numOfAdults=1):  # default classInfo is "ECONOMY" and numOfAdults is 1
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": date,
            "adults": numOfAdults,
            "travelClass": classInfo,
            "currencyCode": "EUR",
            "max": 10
        }

        try:
            response = requests.get(url, headers=headers, params=params)

            # If token expired, refresh it and retry once (401 error → get token again)
            if response.status_code == 401:
                self.token = self.get_access_token()
                headers["Authorization"] = f"Bearer {self.token}"
                response = requests.get(url, headers=headers, params=params)

            if response.status_code == 400 and "INVALID DATE" in response.text:
                # Flight not found: invalid date may have been entered
                return {"data": []}

            if response.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"API Error {response.status_code}: {response.text}",
                    response=response
                )

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error: {http_err}")
            return {
                "error": str(http_err),
                "status_code": response.status_code if response else 500
            }

        except Exception as err:
            print(f"Unexpected error: {err}")
            return {
                "error": str(err),
                "status_code": 500
            }



# For Currency Conversion 
#-------------------------------------------------------------------
def get_latest_rates(base_currency="EUR"):
    url = f"https://api.frankfurter.app/latest?from={base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rates = data.get("rates", {})
        rates[base_currency] = 1.0 
        return rates
    else:
        print(f"API error: {response.status_code}")
        return None

def convert_currency(amount, from_currency, to_currency):
    rates = get_latest_rates(base_currency=from_currency)
    if rates is None:
        raise Exception("Failed to get exchange rates")
    if to_currency not in rates:
        raise Exception(f"Currency {to_currency} not found in rates")
    return amount * rates[to_currency]

