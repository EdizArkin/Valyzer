import sys
import os
# Add project root to sys.path (Valyzer folder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
from datetime import date, timedelta
import streamlit_toggle as tog
from src.travel.travel_service import TravelService


# Service katmanından havaalanı verisini al
service = TravelService()
airports = service.get_airports()

# Streamlit UI
st.title("✈️ Travel Price Forecast")

origin = st.selectbox("Origin", options=airports, key="travel_origin")
destination = st.selectbox("Destination", options=airports, key="travel_destination")

today = date.today()
is_round_trip = st.toggle(value=False, label="", key="toggle")

# Toggle label'ını dinamik göster
if is_round_trip:
    st.write("**Round-trip**")
else:
    st.write("**One-way**")

if is_round_trip:
    travel_date = st.date_input(
        "Departure Date",
        value=today,
        min_value=today,
        key="departure_date"
    )
    # Dönüş tarihinin en erken seçilebileceği tarih = gidiş tarihinden 1 gün sonrası
    min_return_date = travel_date + timedelta(days=1)
    return_date = st.date_input(
        "Return Date",
        value=min_return_date,
        min_value=min_return_date,
        key="return_date"
    )
else:
    travel_date = st.date_input(
        "Travel Date",
        value=today,
        min_value=today,
        key="travel_date"
    )
    return_date = None

# Ekstra kontrol: dönüş tarihi gidiş tarihinden önce veya aynı gün olmamalı
if return_date is not None and return_date <= travel_date:
    st.error("Return date cannot be earlier than or same as departure date.")

st.markdown("---")

if st.button("Forecast Travel Prices"):
    # Placeholder tahmin örneği
    st.info(f"Predicted Airfare: ₺1450\nPredicted Hotel Price: ₺890")
    st.line_chart([1200, 1300, 1375, 1450])
