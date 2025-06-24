import sys
import os
# Add project root to sys.path (Valyzer folder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import streamlit_toggle as tog
from src.services.travel_service import TravelService


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
    placeholder_text = "Please select an airport"
    airport_options = [placeholder_text] + airports

    # Origin selectbox
    origin = st.selectbox(
        "Origin",
        options=airport_options,
        index=0,
        key="travel_origin",
        help="Select your departure airport. The list is not exhaustive, but includes major airports worldwide.\n\n**Tip:** You can type airport codes in Uppercase (e.g. `SAW`), and we'll match them."
    )

    # Check if origin is selected with session_state
    if "origin_selected" not in st.session_state:
        st.session_state.origin_selected = False

    if origin != placeholder_text:
        st.session_state.origin_selected = True
    else:
        st.session_state.origin_selected = False

    # Destination selectbox only show if origin is selected
    if st.session_state.origin_selected:
        destination_options = [placeholder_text] + [a for a in airports if a != origin]
        destination = st.selectbox(
            "Destination",
            options=destination_options,
            index=0,
            key="travel_destination",
            help="Select your arrival airport. The list is not exhaustive, but includes major airports worldwide.\n\n**Tip:** You can type airport codes in Uppercase (e.g. `IST`), and we'll match them."
        )
    else:
        st.info("Please select an origin airport before choosing a destination.")



    # Mapping the values ​​to be sent to the API with the external display
    travel_class_map = {
        "Economy": "ECONOMY",
        "Premium Economy": "PREMIUM_ECONOMY",
        "Business": "BUSINESS",
        "First": "FIRST"
    }

    col_class, col_num_adults_currencies = st.columns([1, 1])
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


    with col_num_adults_currencies:

        col_num_adults, col_num_currencies = st.columns([1, 1])
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
        with col_num_currencies:
            selected_currency = st.selectbox(
                "Currency",
                options=["EUR", "USD", "TRY"],
                index=0,  # Default to EUR
                key="currency",
                help="Select the currency for the prices. The default is Euro (EUR)."
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

# Extra validation for travel dates
if return_date is not None and return_date <= travel_date:
    st.error("Return date cannot be earlier than or same as departure date.")

st.markdown("-----------------------------------------------------------------------------")



if st.button("Forecast Travel Prices"):
    # If origin or destination is not selected, show a warning and set df_prices to an empty DataFrame
    if origin == placeholder_text or destination == placeholder_text:
        st.warning("⚠️ Please select both origin and destination airports before proceeding.")
        df_prices = pd.DataFrame()
    else:
        with st.spinner("Loading travel prices... Please wait"):
            travel_date = travel_date.strftime("%Y-%m-%d")
            travel_class_api_value = travel_class_map[selected_class_display]

            try:
                df_prices = service.get_travel_data(
                    origin=origin,
                    destination=destination,
                    travel_date=travel_date,
                    classInfo=travel_class_api_value,
                    numOfAdults=num_adults,
                    selected_currency=selected_currency
                )
            except Exception as e:
                st.error(f"⚠️ Error fetching flight data: {e}")
                df_prices = pd.DataFrame()


        # If an error is returned from the API or if it's empty, show a warning
        if isinstance(df_prices, dict) and "error" in df_prices:
            status = df_prices.get("status_code", 500)

            if status == 500:
                st.warning("⚠️ Internal Server Error. Please try again later.")
            elif status == 401:
                st.warning("🔒 Authorization failed. Please check your credentials.")
            elif status == 400:
                st.warning("✈️ No flights found for the selected route and date.")
            else:
                st.warning(f"⚠️ An unexpected error occurred (code: {status}).")
            df_prices = pd.DataFrame()  # To avoid UI crash with empty dataframe afterwards

        elif isinstance(df_prices, pd.DataFrame) and df_prices.empty:
            st.warning("✈️ No flights found for the selected route and date.")


    # If df_prices is not empty, show table and graph
    if isinstance(df_prices, pd.DataFrame) and not df_prices.empty:
        col1, col2 = st.columns([15, 15], gap="large")

        with col1:
            st.subheader("📊 Price Table")
            st.dataframe(df_prices)
            print(df_prices.head())  # Debugging: Print the first few rows of the DataFrame to console

        with col2:
            st.subheader("📈 Price Trend")
            st.line_chart(df_prices.set_index("date")["price"])
            st.markdown("**Note:** The prices are indicative and may vary based on real-time availability and booking conditions.")
            st.markdown(
                "**Note:** <span style='color:red'>There may be minor changes in currency exchanges depending on the provider's data!</span>",
                unsafe_allow_html=True
            )

# Weather information section


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


def render_weather_card(weather, city, is_placeholder=False):
    if is_placeholder:
        st.markdown(
            f"""
            <div style='
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 10px;
                background-color: #f0f0f0;
                margin-bottom: 10px;
                text-align: center;
                opacity: 0.4;
            '>
                <h4 style='margin-bottom: 5px'>{city}</h4>
                <p style='margin: 0; font-size: 16px; color: grey;'>Not selected</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif weather:
        st.markdown(
            f"""
            <div style='
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 10px;
                background-color: #f9f9f9;
                margin-bottom: 10px;
                text-align: center;
            '>
                <h4 style='margin-bottom: 5px'>{weather["city"]}</h4>
                <img src='{weather["icon"]}' width='50'>
                <p style='margin: 0; font-size: 20px;'>{weather["temp"]}°C</p>
                <p style='font-size: 14px; color: grey'>{weather["desc"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Weather data could not be loaded.")


with st.sidebar:
    st.subheader("🌤 Weather Info")

    # Origin hava durumu
    if "travel_origin" not in st.session_state or st.session_state.travel_origin == placeholder_text:
        render_weather_card(None, "Origin", is_placeholder=True)
    else:
        origin = st.session_state.travel_origin
        origin_weather = service.get_weather(extract_city_name(origin))
        render_weather_card(origin_weather, extract_city_name(origin))

    # Destination hava durumu
    if "travel_destination" not in st.session_state or st.session_state.travel_destination == placeholder_text:
        render_weather_card(None, "Destination", is_placeholder=True)
    else:
        destination = st.session_state.travel_destination
        destination_weather = service.get_weather(extract_city_name(destination))
        render_weather_card(destination_weather, extract_city_name(destination))


