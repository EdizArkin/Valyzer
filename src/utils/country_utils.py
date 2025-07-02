import pycountry
import re
import pandas as pd
import holidays
from src.config.config import RAW_DATA_PATH

def extract_iata(airport_str):
        match = re.search(r'\((\w{3})\)', airport_str)
        return match.group(1) if match else airport_str

def country_name_to_code(country_name: str) -> str:
    """
    Converts country name to 2-letter ISO country code (e.g., "Turkey" → "TR")
    """
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            # fallback: try partial match
            for c in pycountry.countries:
                if country_name.lower() in c.name.lower():
                    return c.alpha_2
            return "XX"
        return country.alpha_2
    except Exception as e:
        print(f"[Country Code] Error: {e}")
        return "XX"


def extract_city_name(city_str):
        """
        Extracts city name from strings like 'Baruun Urt Airport (UUN)' or 'London, United Kingdom'.
        Removes airport codes and trims whitespace or generic suffixes like 'Airport'.
        """
        # 1. Remove text in parentheses (e.g., "(UUN)")
        if "(" in city_str:
            city_str = city_str.split("(")[0].strip()
            #print(f"Debug: After removing parentheses, city_str = '{city_str}'")  # Debugging

        # 2. Remove "Airport" suffix if present
        if "Airport" in city_str:
            city_str = city_str.replace("Airport", "").strip()
            #print(f"Debug: After removing 'Airport', city_str = '{city_str}'")  # Debugging

        # 3. Remove any trailing text after a hyphen (e.g., "Baruun Urt - Airport")
        if "-" in city_str:
            city_str = city_str.split("-")[0].strip()
            #print(f"Debug: After splitting by hyphen, city_str = '{city_str}'")  # Debugging


        # 4. If still has comma (like 'London, United Kingdom'), take the first part
        if "," in city_str:
            city_str = city_str.split(",")[0].strip()
            #print(f"Debug: After splitting by comma, city_str = '{city_str}'")  # Debugging

        return city_str


def get_country_code_from_iata(iata_code: str) -> str:
    """
    Looks up the country code (ISO 2-letter) for a given IATA code.
    """
    try:
        airports_data_path = f"{RAW_DATA_PATH}/airports.csv"
        df = pd.read_csv(airports_data_path, header=None)
        df.columns = [
            "id", "name", "city", "country", "iata_code", "icao_code",
            "lat", "lon", "alt", "tz_offset", "dst", "tz", "type", "source"
        ]
        row = df[df["iata_code"] == iata_code.upper()]
        if not row.empty:
            country_name = row.iloc[0]["country"]
            return country_name_to_code(country_name)
        else:
            raise ValueError(f"IATA code not found: {iata_code}")
    except Exception as e:
        print(f"[IATA Lookup] Error: {e}")
        return "XX"


def get_holidays(date_start, iata_code, year, date_end=None):
    """
    Fetches holidays for the specified country and date range.
    Returns a list of holidays within the date range.
    """
    try:
        country_code = get_country_code_from_iata(iata_code)
        if not country_code or country_code == "XX":
            return []

        # Eğer date_end None ise, date_end = date_start yap (tek gün için)
        if date_end is None:
            date_end = date_start

        # Initialize the holidays object for the specified country
        country_holidays = holidays.CountryHoliday(country_code, years=year)

        # Filter holidays within the specified date range
        filtered_holidays = [
            (date, name) for date, name in country_holidays.items()
            if date_start <= date <= date_end
        ]

        return filtered_holidays
    except Exception as e:
        print(f"[Holiday Service] Error fetching holidays: {e}")
        return []

