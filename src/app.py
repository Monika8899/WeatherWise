import streamlit as st
import os
from dotenv import load_dotenv
from weather_service import get_weather, get_forecast
import webbrowser

# Load API key from .env
load_dotenv()

# Open browser automatically on localhost
if not os.environ.get("STREAMLIT_BROWSER_OPENED"):
    webbrowser.open("http://localhost:8501")
    os.environ["STREAMLIT_BROWSER_OPENED"] = "1"

# Streamlit UI setup
st.set_page_config(page_title="WeatherWise", page_icon="⛅", layout="wide")
st.title("🌤️ WeatherWise")
st.write("🌍 Get Real-Time Weather Updates and Fun Weather Tips!")

# Sidebar: Enter City Name
st.sidebar.header("🌆 Enter City Name")
selected_city = st.sidebar.text_input("Type a city name", "")

if selected_city:
    st.header(f"Weather in {selected_city}")
    weather_data = get_weather(selected_city)
    forecast_data = get_forecast(selected_city)

    if "error" in weather_data:
        st.error(weather_data["error"])
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Temperature", weather_data["temperature"])
        col2.metric("💧 Humidity", weather_data["humidity"])
        col3.metric("💨 Wind Speed", weather_data["wind_speed"])
        col4.metric("☁️ Condition", weather_data["condition"])

        # Fun weather messages
        condition = weather_data["condition"].lower()
        if "rain" in condition:
            st.info("☔ It's going to rain! Perfect time for chai and pakoras!")
        elif "clear" in condition:
            st.success("☀️ The sun is out! Go touch some grass! 🌱")
        elif "snow" in condition:
            st.warning("❄️ Snow outside? Time to build a snowman! ☃️")
        elif "cloud" in condition:
            st.info("⛅ Clouds? Just enough drama for a Bollywood scene! 🎬")
        else:
            st.info("🌎 Stay prepared for anything today!")

        # Weekly Forecast Section
        st.subheader("📅 7-Day Forecast")
        if "error" in forecast_data:
            st.error(forecast_data["error"])
        else:
            for day in forecast_data:
                st.write(f"📆 {day['date']} - {day['condition']} - 🌡️ {day['temperature']}")

st.write("🚀 Built with ❤️ using Streamlit & Railway PostgreSQL")
