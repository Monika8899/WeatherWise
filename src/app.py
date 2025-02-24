import streamlit as st
import os
from dotenv import load_dotenv
import webbrowser
import plotly.express as px
import pandas as pd
from weather_service import get_weather, get_forecast
from database import (
    init_db,
    save_weather_data,
    get_or_create_user
)
import random

# Load environment variables and initialize
load_dotenv()
init_db()

# Weather message collections
RAIN_MESSAGES = [
    "🌧️ Perfect excuse for a cozy coffee date! Time to channel your inner romantic poet! ☔",
    "🌧️ Dancing in the rain? More like Netflix and staying dry! 🛋️",
    "🌧️ Time to test if your umbrella has secret leaks! 🕵️‍♂️",
    "🌧️ Mother Nature's way of watering her plants... and your new hairstyle! 💁‍♂️",
    "🌧️ Perfect weather for writing that novel you've been putting off! 📚",
    "🌧️ Grab your raincoat and embrace your inner storm chaser! 🌪️",
    "🌧️ Indoor picnic day! Because who needs dry grass anyway? 🧺",
    "🌧️ Time to perfect your splash-dodging dance moves! 💃",
    "🌧️ Your plants are doing a happy dance right now! 🌿",
    "🌧️ The perfect excuse to order that comfort food delivery! 🍜"
]

SNOW_MESSAGES = [
    "❄️ Do you wanna build a snowman? Or maybe just stay inside with hot cocoa? ⛄",
    "❄️ Time to perfect your 'walking on ice' technique! 🏃‍♂️",
    "❄️ Snow way! Time to channel your inner penguin! 🐧",
    "❄️ Perfect weather for your best snow angel impression! 👼",
    "❄️ Time to test if your gloves are really waterproof! 🧤",
    "❄️ Snowball fight, anyone? Choose your team wisely! 🎯",
    "❄️ Hot chocolate season is officially in session! ☕",
    "❄️ Time to show off those winter fashion layers! 🧣",
    "❄️ Your car might need a snow blanket today! 🚗",
    "❄️ Perfect day for indoor fort building! 🏰"
]

CLEAR_HOT_MESSAGES = [
    "☀️ Sunglasses? Check. Sunscreen? Check. Summer vibes? Double check! 🕶️",
    "☀️ Hot enough to fry an egg on the sidewalk! (Please don't try) 🍳",
    "☀️ Time to become best friends with your AC! 🌡️",
    "☀️ Beach day alert! Time to work on those sandcastle skills! 🏖️",
    "☀️ Perfect weather for ice cream... or two... or three! 🍦",
    "☀️ Your plants might need an extra drink today! 🌿",
    "☀️ Time to test if your sunscreen really is waterproof! 🏊‍♂️",
    "☀️ Perfect day for a rooftop party! Just bring extra water! 🎉",
    "☀️ Warning: Hot weather may cause spontaneous pool parties! 💦",
    "☀️ Time to show off those summer fashion choices! 👕"
]

CLEAR_MILD_MESSAGES = [
    "🌤️ Perfect weather for everything! Literally everything! 🎯",
    "🌤️ Mother Nature showing off her perfect weather skills! 🌈",
    "🌤️ Time for that picnic you've been planning forever! 🧺",
    "🌤️ Perfect day for outdoor yoga... or napping in the park! 🧘‍♀️",
    "🌤️ Weather so nice, even your phone wants to go outside! 📱",
    "🌤️ Time to dust off that bicycle! 🚲",
    "🌤️ Picture perfect weather for your social media feed! 📸",
    "🌤️ Nature's way of saying 'go touch some grass'! 🌱",
    "🌤️ Perfect weather for a spontaneous adventure! 🗺️",
    "🌤️ Time to write poetry under a tree! 📝"
]

CLOUDY_MESSAGES = [
    "☁️ The clouds are playing hide and seek with the sun! 🎭",
    "☁️ Fifty shades of grey... in the sky! 🎨",
    "☁️ Perfect lighting for your moody photoshoot! 📸",
    "☁️ The sun is just taking a quick nap behind the clouds! 😴",
    "☁️ Cloud-watching day! That one looks like a dragon! 🐉",
    "☁️ Nature's way of providing natural shade! ⛅",
    "☁️ Time for some cloud appreciation! 🤍",
    "☁️ Perfect weather for a mysterious movie scene! 🎬",
    "☁️ The sky's version of a cozy blanket! 🛏️",
    "☁️ Clouds gathering for their daily meeting! 📊"
]


def get_rotating_message(message_list):
    """Get a random message from the list to ensure variety."""
    return random.choice(message_list)


def generate_fun_forecast_message(forecast_data):
    """Generate fun messages based on weather forecast with rotation."""
    messages = []
    for day in forecast_data:
        condition = day['condition'].lower()
        temp = float(day['temperature'].replace('°C', ''))
        date = day['date']

        if 'rain' in condition:
            message = get_rotating_message(RAIN_MESSAGES)
        elif 'snow' in condition:
            message = get_rotating_message(SNOW_MESSAGES)
        elif 'clear' in condition and temp > 25:
            message = get_rotating_message(CLEAR_HOT_MESSAGES)
        elif 'clear' in condition and temp <= 25:
            message = get_rotating_message(CLEAR_MILD_MESSAGES)
        elif 'cloud' in condition:
            message = get_rotating_message(CLOUDY_MESSAGES)
        else:
            message = f"🌈 Weather's keeping it interesting! Like a box of chocolates, you never know what you're gonna get! 🍫"

        messages.append(f"{date}: {message}")

    return messages


# Page configuration
st.set_page_config(
    page_title="WeatherWise Pro",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
        .main {
            padding: 0rem 1rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .st-emotion-cache-16idsys p {
            font-size: 20px;
            margin-bottom: 10px;
        }
        div[data-testid="stMetricValue"] {
            font-size: 28px;
        }
        .metric-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-bottom: 1rem;
            height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .metric-card h3 {
            margin-bottom: 15px;
            font-size: 1.2rem;
            white-space: nowrap;
        }
        .metric-card h2 {
            font-size: 1.8rem;
            margin: 0;
            white-space: nowrap;
        }
        .forecast-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }
        .forecast-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            height: 180px;     /* Fixed height */
            width: 100%;       /* Full width of column */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .forecast-date {
            font-weight: bold;
            color: #1E88E5;
            font-size: 14px;
            margin-bottom: 8px;
            white-space: nowrap;
        }
        .forecast-temp {
            font-size: 24px;
            margin: 10px 0;
            font-weight: bold;
        }
        .forecast-condition {
            color: #666;
            margin-bottom: 8px;
            white-space: nowrap;
        }
        .forecast-data {
            margin: 4px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Main title and description
st.title("🌤️ WeatherWise Pro")
st.write("Your Smart Weather Companion - Now with Extra Fun! 🌍")

# City Selection in main area
st.markdown("<h3 style='margin-bottom: 5px;'>Enter City Name</h3>", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    selected_city = st.text_input("", placeholder="Type a city name...",
                                 label_visibility="collapsed",
                                 help="Enter the name of any city to get weather updates!")
with col2:
    if st.button("🔍 Get Weather", key="get_weather_btn"):
        st.session_state.selected_city = selected_city

#  CSS to ensure straight alignment
st.markdown("""
    <style>
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    
    div[data-testid="stTextInput"] {
        width: 100%;
    }
    
    div.stButton {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Optional User Login in sidebar
with st.sidebar:
    st.header("👤 User Area (Optional)")
    with st.expander("Login / Register"):
        username = st.text_input("Enter your name", key="username_input")
        if username:
            user = get_or_create_user(username)
            if user:
                st.success(f"Welcome, {username}! 🎉")
                st.session_state.user = user
            else:
                st.error("Login error. Please try again.")

# Main weather display
if selected_city:
    weather_data = get_weather(selected_city)
    forecast_data = get_forecast(selected_city)

    if "error" in weather_data:
        st.error(f"🚫 {weather_data['error']}")
    else:
        # Current Weather Display with better styling
        st.markdown("### Current Weather")
        cols = st.columns([1,1,1,1])

        metrics = [
            ("Temperature", weather_data["temperature"], "🌡️"),
            ("Humidity", weather_data["humidity"], "💧"),
            ("Wind Speed", weather_data["wind_speed"], "💨"),
            ("Condition", weather_data["condition"], "☁️")
        ]

        for col, (label, value, icon) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>{icon} {label}</h3>
                        <h2>{value}</h2>
                    </div>
                """, unsafe_allow_html=True)

        # Save data for analytics
        temp_value = float(weather_data["temperature"].replace("°C", ""))
        save_weather_data(selected_city, temp_value, weather_data["condition"])

        # Forecast Plot
        st.markdown("### 📊 7-Day Forecast")
        if isinstance(forecast_data, list) and forecast_data:
            forecast_df = pd.DataFrame([
                {
                    'date': day['date'],
                    'temperature': float(day['temperature'].replace('°C', '')),
                    'condition': day['condition']
                }
                for day in forecast_data
            ])

            forecast_fig = px.line(
                forecast_df,
                x='date',
                y='temperature',
                markers=True
            )

            forecast_fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Temperature (°C)",
                hovermode='x unified',
                showlegend=False,
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                title_text="Temperature Forecast",
                title_x=0.5
            )

            # Add weather conditions as annotations
            for idx, row in forecast_df.iterrows():
                forecast_fig.add_annotation(
                    x=row['date'],
                    y=row['temperature'],
                    text=row['condition'].split()[-1],
                    showarrow=False,
                    yshift=10
                )

            st.plotly_chart(forecast_fig, use_container_width=True)

            # Weekly Forecast Details
            st.markdown("### 📅 Weekly Forecast")
            forecast_cols = st.columns(min(len(forecast_data), 7))

            for day, col in zip(forecast_data, forecast_cols):
                with col:
                    st.markdown(f"""
                        <div class="forecast-card">
                            <div class="forecast-date">{day['date']}</div>
                            <div class="forecast-temp">{day['temperature']}</div>
                            <div class="forecast-condition">{day['condition']}</div>
                            {f"<div>💧 {day['humidity']}</div>" if 'humidity' in day else ""}
                            {f"<div>💨 {day['wind_speed']}</div>" if 'wind_speed' in day else ""}
                        </div>
                    """, unsafe_allow_html=True)

            # Fun weather insights
            st.markdown("### 🎯 Weather Insights")
            fun_messages = generate_fun_forecast_message(forecast_data)
            for msg in fun_messages:
                st.info(msg)

            # Weather Tips
            st.markdown("### 💡 Weather Tips")
            current_condition = weather_data["condition"].lower()
            current_temp = float(weather_data["temperature"].replace("°C", ""))

            if 'rain' in current_condition:
                st.warning("🌂 Don't forget your umbrella!")
                st.info("🎮 Great day for indoor activities!")
            elif 'snow' in current_condition:
                st.warning("🧤 Bundle up! It's cold outside!")
                st.info("☕ Perfect for hot beverages!")
            elif 'clear' in current_condition and current_temp > 25:
                st.warning("🧴 Don't forget sunscreen!")
                st.info("💦 Stay hydrated!")
            else:
                st.success("👍 Great weather for outdoor activities!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 10px;'>
        <p>Made with ❤️ using Streamlit & Railway PostgreSQL</p>
    </div>
    """,
    unsafe_allow_html=True
)