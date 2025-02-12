import streamlit as st
import requests
from error_handling import fetch_weather  

#  API Key
API_KEY = "067d8918137138efbb6c1584556bab8d"

st.set_page_config(
    page_title="WeatherWise",
    page_icon="⛅",
    layout="wide"
)

# Main title and description
st.title("WeatherWise")
st.write("See Real-Time Weather and a Quick Three-Day Forecast.")

#  City select box 
st.sidebar.header("Enter City Name")
selected_city = st.sidebar.text_input("Type a city name", "")

#  Fetch Weather when user Enters a City name
if selected_city:
    st.header(f"Weather Information for {selected_city}")

    try:
        # Fetchhing current weather 
        current_weather = fetch_weather(selected_city, API_KEY)

        if current_weather:
            # Displaying  Current Weather
            st.subheader("Current Weather")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Temperature (°C)", current_weather["temperature"])
            col2.metric("Humidity (%)", current_weather["humidity"])
            col3.metric("Wind Speed (km/h)", current_weather["wind_speed"])
            col4.metric("Condition", current_weather["condition"])

    except Exception as e:
        st.error(" An unexpected error occurred. Please try again later.")
        st.error(f"Error details: {e}")

else:
    st.warning("Please enter a city name to get the weather data.")
