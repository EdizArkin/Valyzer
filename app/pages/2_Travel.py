import streamlit as st
from datetime import date

import sys
import os

# Proje kökünü sys.path'e ekle (Valyzer klasörü)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.travel.travel_service import TravelService



# Service katmanından havaalanı verisini al
service = TravelService()
airports = service.get_airports()

# Streamlit UI
st.title("✈️ Travel Price Forecast")

origin = st.selectbox("Origin", options=airports, key="travel_origin")
destination = st.selectbox("Destination", options=airports, key="travel_destination")
travel_date = st.date_input("Travel Date", value=date.today(), key="travel_date")

if st.button("Forecast Travel Prices"):
    # Placeholder tahmin örneği
    st.info(f"Predicted Airfare: ₺1450\nPredicted Hotel Price: ₺890")
    st.line_chart([1200, 1300, 1375, 1450])
