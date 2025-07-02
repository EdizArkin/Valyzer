import requests
import re
from datetime import date, datetime, timedelta
import pandas as pd
from src.config.config import AMADEUS_API_KEY, AMADEUS_API_SECRET
from src.utils.country_utils import extract_iata

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
        origin_code = extract_iata(origin)
        destination_code = extract_iata(destination)

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
                            converted_price = self.convert_currency(float(price), 'EUR', selected_currency)
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
    # This function fetches the latest exchange rates from the Frankfurter API
    #-------------------------------------------------------------------
    def get_latest_rates(self, base_currency="EUR"):
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

    def convert_currency(self, amount, from_currency, to_currency):
        rates = self.get_latest_rates(base_currency=from_currency)
        if rates is None:
            raise Exception("Failed to get exchange rates")
        if to_currency not in rates:
            raise Exception(f"Currency {to_currency} not found in rates")
        return amount * rates[to_currency]


    #-------------------------------------------------------------------
    # For City Coordinates
    # Destination Experiences API by Amadeus

    def get_city_coordinates(self, city_name):
        url = "https://test.api.amadeus.com/v1/reference-data/locations"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "keyword": city_name,
            "subType": "CITY"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        if not data.get("data"):
            print(f"[WARN] No data found for city: {city_name}")
            return None, None

        location = data["data"][0]["geoCode"]
        lat = location["latitude"]
        lon = location["longitude"]
        return lat, lon


    #-------------------------------------------------------------------
    # For Destination Activities
    def fetch_destination_activities(self, city_name):
        try:
            lat, lon = self.get_city_coordinates(city_name)

            if not lat or not lon:
                print(f"[WARN] Coordinates could not be obtained: {city_name}")
                return []

            response = requests.get(
                "https://test.api.amadeus.com/v1/shopping/activities",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"latitude": lat, "longitude": lon, "radius": 20}
            )
            response.raise_for_status()
            return response.json().get("data", [])

        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Amadeus API error: {e}")
            return []

        except Exception as e:
            print(f"[ERROR] Unknown error: {e}")
            return []


    #-------------------------------------------------------------------
    # For Hotels
    # This function fetches hotels in a city

    def fetch_hotels_by_city(self, destination):
        """
        Fetches hotel data for a given destination city using its IATA code.
        Returns a list of hotel dictionaries with ratings (up to 3 rated hotels).
        """
        try:
            city_iata_code = extract_iata(destination)
            response = requests.get(
                f"https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city?cityCode={city_iata_code}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            hotels = response.json().get("data", [])

            if not hotels:
                print(f"[WARN] No hotels found for city: {city_iata_code}")
                return []

            # Get ratings only with first 10 hotel IDs
            hotel_ids = [hotel.get("hotelId") for hotel in hotels if "hotelId" in hotel][:10]
            ratings = self.get_hotel_ratings(hotel_ids)

            # Match rating data by ID (if rating exists)
            rating_map = {r["hotelId"]: r for r in ratings}

            # Add ratings to hotel objects
            for hotel in hotels:
                hotel_id = hotel.get("hotelId")
                if hotel_id in rating_map:
                    hotel["ratings"] = rating_map[hotel_id]
                else:
                    hotel["ratings"] = None  # rating not found

            return hotels

        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Amadeus API error: {e}")
            return []

        except Exception as e:
            print(f"[ERROR] Unknown error: {e}")
            return []



    def get_hotel_ratings(self, hotel_ids):
        """
        Fetches hotel ratings for a list of hotel IDs in batches of 3.
        Returns a list of rating data dictionaries.
        """
        all_ratings = []
        
        if not hotel_ids:
            return []

        try:
            # Batch the hotel IDs to avoid hitting API limits
            batch_size = 3
            for i in range(0, len(hotel_ids), batch_size):
                batch = hotel_ids[i:i+batch_size]
                hotel_ids_str = ",".join(batch)
                
                response = requests.get(
                    "https://test.api.amadeus.com/v2/e-reputation/hotel-sentiments",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"hotelIds": hotel_ids_str}
                )
                if response.status_code == 200:
                    ratings = response.json().get("data", [])
                    all_ratings.extend(ratings)
                elif response.status_code == 429:
                    print(f"[WARN] Rate limit exceeded, FREE QUOTA EXCEEDED")
                else:
                    print(f"[ERROR] Rating fetch failed for batch {batch}: {response.status_code} {response.reason}")
        except Exception as e:
            print(f"[ERROR] Unknown error during rating fetch: {e}")

        return all_ratings


