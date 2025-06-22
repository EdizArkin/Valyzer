import sys
import os
# Add project root to sys.path (Valyzer folder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
from datetime import date, timedelta
import streamlit_toggle as tog
from src.travel.travel_service import TravelService

# Set Streamlit page configuration
st.set_page_config(layout="wide")


# Retrieve airport data from service layer
service = TravelService()
airports = service.get_airports()

# Streamlit UI
st.title("✈️ Travel Price Forecast")

# make orgigin and destination UN-keysensitive
origin = st.selectbox(
    "Origin", 
    options=airports,
    key="travel_origin",
    help="Select your departure airport. The list is not exhaustive, but includes major airports worldwide."
)
st.markdown("**Tip:** You can type airport codes in Uppercase (e.g. `SAW`), and we'll match them.")

destination = st.selectbox(
    "Destination",
    options=airports,
    key="travel_destination",
    help="Select your arrival airport. The list is not exhaustive, but includes major airports worldwide."
)
st.markdown("**Tip:** You can type airport codes in Uppercase (e.g. `IST`), and we'll match them.")


today = date.today()
is_round_trip = st.toggle(value=False, label="", key="toggle", help="Toggle to switch between one-way and round-trip travel.")

# Show toggle label dynamically
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
    # Earliest date to choose for return = 1 day after departure date
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

# Extra check: return date should not be before or on the same day as departure date
if return_date is not None and return_date <= travel_date:
    st.error("Return date cannot be earlier than or same as departure date.")

st.markdown("-----------------------------------------------------------------------------")



if st.button("Forecast Travel Prices"):
    travel_date = travel_date.strftime("%Y-%m-%d")
    #print(travel_date) # Debugging line to check travel_date format
    df_prices = service.get_travel_data(origin=origin, destination=destination, travel_date=travel_date)

    #----------------------------------------------------
    # For Testing purposes, using hardcoded values
    #df = service.get_travel_data("Istanbul (IST)", "Berlin (BER)", "2025-07-22")
    
    col1, col2 = st.columns([15, 15], gap="large")

    with col1:
        st.subheader("📊 Price Table")
        st.dataframe(df_prices)

    with col2:
        st.subheader("📈 Price Trend")
        st.line_chart(df_prices.set_index("date")["price"])
