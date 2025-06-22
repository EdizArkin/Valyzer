'''
Scraper for travel-related data.
This module is designed to scrape flight data from various sources, providing users with information about flight prices, schedules, and other relevant details.
For each flight:

Data for ±7 days of the selected date (14-day window)

If possible, information such as time, airline, number of stops
'''

import requests


# src/travel/travel_scraper.py

from datetime import datetime, timedelta
import random
import pandas as pd

def fetch_travel_data(origin, destination, travel_date, days_window=7):
    """
    Simulates fetching flight prices from travel platforms.
    Returns a DataFrame with simulated flight prices from -days to +days window.
    """

    base_date = datetime.strptime(travel_date, "%Y-%m-%d")
    date_range = [base_date + timedelta(days=i) for i in range(-days_window, days_window+1)]

    prices = []
    for date in date_range:
        price = random.randint(3000, 6000)  # Simulated price in TRY
        prices.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": price,
            "origin": origin,
            "destination": destination,
            "days_until_flight": (date - datetime.today()).days
        })

    df = pd.DataFrame(prices)
    return df
