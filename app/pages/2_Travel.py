import streamlit as st
from datetime import date

st.title("✈️ Travel Price Forecast")

origin = st.text_input("Origin", key="travel_origin")
destination = st.text_input("Destination", key="travel_destination")
travel_date = st.date_input("Travel Date", value=date.today(), key="travel_date")

if st.button("Forecast Travel Prices"):
    # Placeholder for forecast logic
    st.info("Predicted Airfare: ₺1450\nPredicted Hotel Price: ₺890")
    st.line_chart([1200, 1300, 1375, 1450])
