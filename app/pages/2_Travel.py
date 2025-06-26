import sys
import os
import random
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

# Helper to display warnings based on API errors
def check_and_warn(df, label=""):
    if isinstance(df, dict) and "error" in df:
        status = df.get("status_code", 500)
        if status == 500:
            st.warning(f"⚠️ {label}Internal Server Error.")
        elif status == 401:
            st.warning(f"🔒 {label}Authorization failed.")
        elif status == 400:
            st.warning(f"✈️ {label}No flights found.")
        else:
            st.warning(f"⚠️ {label}Unexpected error (code: {status}).")
        return pd.DataFrame()
    elif isinstance(df, pd.DataFrame) and df.empty:
        st.warning(f"✈️ {label}No flights found.")
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


# Caching the travel data retrieval function to optimize performance
# This will cache the results for 45 minutes (2700 seconds)
@st.cache_data(ttl=2700, show_spinner=False)
def get_cached_travel_data(origin, destination, travel_date, classInfo, numOfAdults, selected_currency,):
    return service.get_travel_data(
        origin=origin,
        destination=destination,
        travel_date=travel_date,
        classInfo=classInfo,
        numOfAdults=numOfAdults,
        selected_currency=selected_currency
    )

# Caching the activities retrieval function to optimize performance
# This will cache the results for 15 minutes (900 seconds)
@st.cache_data(ttl=900, show_spinner=False)
def get_cached_activities(city_name):
    return service.get_destination_activities(city_name)


# Initialize session state for dataframes if not already present
if "df_departure" not in st.session_state: 
    st.session_state["df_departure"] = pd.DataFrame(); 
if "df_return" not in st.session_state: 
    st.session_state["df_return"] = pd.DataFrame(); 


# Button clicked
if st.button("Forecast Travel Prices"):
    if origin == placeholder_text or destination == placeholder_text:
        st.warning("⚠️ Please select both origin and destination airports before proceeding.")
        st.session_state["df_departure"] = pd.DataFrame()
        st.session_state["df_return"] = pd.DataFrame()
    else:
        with st.spinner("Loading travel prices... Please wait"):
            travel_class_api_value = travel_class_map[selected_class_display]
            travel_date_str = travel_date.strftime("%Y-%m-%d")
            return_date_str = return_date.strftime("%Y-%m-%d") if is_round_trip else None

            try:
                # Departure
                df_departure = get_cached_travel_data(
                    origin=origin,
                    destination=destination,
                    travel_date=travel_date_str,
                    classInfo=travel_class_api_value,
                    numOfAdults=num_adults,
                    selected_currency=selected_currency
                )

                # Return
                df_return = None
                if is_round_trip:
                    df_return = get_cached_travel_data(
                        origin=destination,
                        destination=origin,
                        travel_date=return_date_str,
                        classInfo=travel_class_api_value,
                        numOfAdults=num_adults,
                        selected_currency=selected_currency
                    )
            except Exception as e:
                st.error(f"⚠️ Error fetching flight data: {e}")
                df_departure = pd.DataFrame()
                df_return = pd.DataFrame()

            # Check and store results
            st.session_state["df_departure"] = check_and_warn(df_departure, "Departure - ")
            st.session_state["df_return"] = check_and_warn(df_return, "Return - ") if is_round_trip else pd.DataFrame()

            
            #!!!!!!!!!!!!! When I press return, the page is still refreshed instead of showing it and the return planes are not shown.

            # DISPLAY RESULTS
            df_departure = st.session_state["df_departure"]
            df_return = st.session_state.get("df_return", pd.DataFrame())

            if not df_departure.empty:
                if is_round_trip and not df_return.empty:
                    trip_option = st.radio(
                        "Select flight direction",
                        ["Departure", "Return"],
                        horizontal=True
                    )
                    current_df = df_departure if trip_option == "Departure" else df_return
                else:
                    current_df = df_departure

                col1, col2 = st.columns([15, 15], gap="large")

                with col1:
                    st.subheader("📊 Price Table")
                    st.dataframe(current_df)

                with col2:
                    st.subheader("📈 Price Trend")
                    st.line_chart(current_df.set_index("date")["price"])
                    st.markdown("**Note:** The prices are indicative and may vary based on real-time availability and booking conditions.")
                    st.markdown("**Note:** <span style='color:red'>There may be minor changes in currency exchanges depending on the provider's data!</span>", unsafe_allow_html=True)


            selected_city = service.extract_city_name(destination)
            if selected_city:
                activities = get_cached_activities(selected_city)

                if not activities or not isinstance(activities, list):
                    st.info("❗ No activities found for the selected city. Please try another city or check back later.")
                else:
                    # Description'ı olmayan aktiviteleri filtrele
                    activities = [a for a in activities if a.get("description")]

                    if activities:
                        st.markdown(f"### 🎯 Things to Do in {selected_city}")
                        # Rastgele 3 aktivite seç
                        sample_activities = random.sample(activities, min(3, len(activities)))

                        for activity in sample_activities:

                            if "pictures" in activity and isinstance(activity["pictures"], list) and activity["pictures"]:
                                image_urls = activity.get("pictures", [])[:5]  # İlk 5 resmi al
                            
                            st.markdown(f"""
                                <div style='
                                    border: 1px solid #ddd;
                                    border-radius: 12px;
                                    padding: 15px;
                                    margin-bottom: 15px;
                                    background-color: #fefefe;
                                    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                                '>
                                    <h4 style='margin-bottom: 8px; color: #333;'>{activity.get("name", "Untitled")}</h4>
                                    <p style='margin: 0; font-size: 15px; color: #555;'>{activity.get("description")}</p>
                                    <div style='display: flex; gap: 10px; margin-bottom: 15px;'>
                                    {''.join([f"<img src='{url}' style='width: 200px; height: 200px; object-fit: cover; border-radius: 6px;'/>" for url in image_urls])}
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("❗No activities described for this city were found. Please try another city or check back later.")



#----------------------------------------------------------------------------------------------------------------------------------------
# Weather Information Section
# Streamlit sidebar for weather information


# Caching for optimized weather data retrieval
@st.cache_data(ttl=900, show_spinner=False)  # 15 minute cache
def get_cached_weather(city_name):
    return service.get_weather(city_name)




def render_weather_card(weather, city, is_placeholder=False):
    if is_placeholder:
        st.markdown(
            f"""
            <div style='
                border: 1px solid #ccc;
                padding: 6px;
                border-radius: 8px;
                background-color: #f0f0f0;
                margin-bottom: 8px;
                text-align: center;
                opacity: 0.4;
                font-size: 12px;
            '>
                <h5 style='margin-bottom: 4px'>{city}</h5>
                <p style='margin: 0; font-size: 16px; color: grey;'>Not selected</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif weather and all(k in weather for k in ["city", "temp", "desc", "feels_like", "max_temp", "min_temp", "icon"]):
        st.markdown(
            f"""
            <div style='
                border: 1px solid #ccc;
                padding: 8px;
                border-radius: 8px;
                background-color: #f0f8ff;
                margin-bottom: 10px;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                font-size: 12px;
            '>
                <h5 style='margin-bottom: 6px;'>{weather["city"]}</h5>
                <img src='{weather["icon"]}' width='40' style='margin-bottom: 4px;'>
                <p style='margin: 2px 0; font-size: 18px; font-weight: bold;'>{weather["temp"]}°C</p>
                <p style='margin: 2px 0; font-size: 14px; color: #666;'>{weather["desc"]}</p>
                <p style='margin: 1px 0; font-size: 13px; color: #444;'>Feels like: {weather["feels_like"]}°C</p>
                <p style='margin: 1px 0; font-size: 13px; color: #444;'>Max: {weather["max_temp"]}°C / Min: {weather["min_temp"]}°C</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"🌥️ Weather data could not be loaded for **{city}**.")




with st.sidebar:
    st.subheader("🌤 Today's Weather Info")

    # Origin hava durumu
    if "travel_origin" not in st.session_state or st.session_state.travel_origin == placeholder_text:
        render_weather_card(None, "Origin", is_placeholder=True)
    else:
        origin = st.session_state.travel_origin
        origin_weather = get_cached_weather(service.extract_city_name(origin))
        render_weather_card(origin_weather, service.extract_city_name(origin))

    # Destination hava durumu
    if "travel_destination" not in st.session_state or st.session_state.travel_destination == placeholder_text:
        render_weather_card(None, "Destination", is_placeholder=True)
    else:
        destination = st.session_state.travel_destination
        destination_weather = get_cached_weather(service.extract_city_name(destination))
        render_weather_card(destination_weather, service.extract_city_name(destination))


