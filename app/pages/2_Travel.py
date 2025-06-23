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

# Sütunları tanımla
col_left, col_right = st.columns([1, 1])

with col_left:
    origin = st.selectbox(
        "Origin", 
        options=airports,
        key="travel_origin",
        help="Select your departure airport. The list is not exhaustive, but includes major airports worldwide.\n\n**Tip:** You can type airport codes in Uppercase (e.g. `SAW`), and we'll match them."
    )
    st.markdown("**Tip:** You can type airport codes in Uppercase (e.g. `SAW`), and we'll match them.")

    destination = st.selectbox(
        "Destination",
        options=airports,
        key="travel_destination",
        help="Select your arrival airport. The list is not exhaustive, but includes major airports worldwide.\n\n**Tip:** You can type airport codes in Uppercase (e.g. `IST`), and we'll match them."
    )
    st.markdown("**Tip:** You can type airport codes in Uppercase (e.g. `IST`), and we'll match them.")

    # Mapping the values ​​to be sent to the API with the external display
    travel_class_map = {
        "Economy": "ECONOMY",
        "Premium Economy": "PREMIUM_ECONOMY",
        "Business": "BUSINESS",
        "First": "FIRST"
    }

    col_class, col_num_adults = st.columns([1, 1])
    # Radio buttons in small font, horizontal display
    with col_class:
        selected_class_display = st.radio(
            "Travel Class",
            options=list(travel_class_map.keys()),
            horizontal=True,
            key="travel_class",
            help="Select the class of travel you prefer. The options range from Economy to First Class."
        )

    # Convert the selected class to the API value / for example, "Economy" to "ECONOMY" debugging
    #travel_class_api_value = travel_class_map[selected_class_display]
    #st.write(f"Selected API travel class value: `{travel_class_api_value}`")


    with col_num_adults:
        num_adults = st.number_input(
            "Number of Adults",
            min_value=1,
            max_value=10, # Adjusted max_value to 10 for practical purposes
            value=1,
            step=1,
            key="num_adults",
            help="Enter the number of adults traveling. The maximum allowed is 10."
        )



with col_right:
    today = date.today()
    is_round_trip = st.toggle(value=False, label="Round Trip", key="toggle", help="Toggle to switch between one-way and round-trip travel.")
    
    if is_round_trip:
        col_departure, col_return = st.columns(2)
        with col_departure:
            st.markdown("**Departure**")
            travel_date = st.date_input(
                "Departure Date",
                value=today,
                min_value=today,
                key="departure_date"
            )
        min_return_date = travel_date + timedelta(days=1)
        with col_return:
            st.markdown("**Return**")
            return_date = st.date_input(
                "Return Date",
                value=min_return_date,
                min_value=min_return_date,
                key="return_date"
            )
    else:
        st.markdown("**One-way**")
        travel_date = st.date_input(
            "Travel Date",
            value=today,
            min_value=today,
            key="travel_date"
        )
        return_date = None

# Ekstra kontrol
if return_date is not None and return_date <= travel_date:
    st.error("Return date cannot be earlier than or same as departure date.")

st.markdown("-----------------------------------------------------------------------------")



if st.button("Forecast Travel Prices"):
    with st.spinner("Loading travel prices... Please wait"):
        travel_date = travel_date.strftime("%Y-%m-%d")
        # Convert the selected class to the API value
        travel_class_api_value = travel_class_map[selected_class_display]

        df_prices = service.get_travel_data(origin=origin, destination=destination, travel_date=travel_date, classInfo=travel_class_api_value, numOfAdults=num_adults)
        print(df_prices.head())  # Debugging line to check the fetched data

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
        st.markdown("**Note:** The prices are indicative and may vary based on real-time availability and booking conditions.")
