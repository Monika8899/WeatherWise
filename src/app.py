import streamlit as st
import os
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
import random
from weather_service import get_weather, get_forecast
from database import (
    init_db,
    save_weather_data,
    get_or_create_user,
    get_temperature_trends,
    add_test_historical_data,
    get_user_cities,
    add_user_city,
    remove_user_city
)
from auth import (
    init_auth_db,
    authenticate,
    register_user,
    change_password,
    get_user
)

# Load environment variables and initialize databases
load_dotenv()
init_db()
init_auth_db()

# Weather message collections
RAIN_MESSAGES = [
    "🌧 Perfect excuse for a cozy coffee date! Time to channel your inner romantic poet! ☔",
    "🌧 Dancing in the rain? More like Netflix and staying dry! 🛋",
    "🌧 Time to test if your umbrella has secret leaks! 🕵‍♂",
    "🌧 Mother Nature's way of watering her plants... and your new hairstyle! 💁‍♂",
    "🌧 Perfect weather for writing that novel you've been putting off! 📚",
    "🌧 Grab your raincoat and embrace your inner storm chaser! 🌪",
    "🌧 Indoor picnic day! Because who needs dry grass anyway? 🧺",
    "🌧 Time to perfect your splash-dodging dance moves! 💃",
    "🌧 Your plants are doing a happy dance right now! 🌿",
    "🌧 The perfect excuse to order that comfort food delivery! 🍜"
]

SNOW_MESSAGES = [
    "❄ Do you wanna build a snowman? Or maybe just stay inside with hot cocoa? ⛄",
    "❄ Time to perfect your 'walking on ice' technique! 🏃‍♂",
    "❄ Snow way! Time to channel your inner penguin! 🐧",
    "❄ Perfect weather for your best snow angel impression! 👼",
    "❄ Time to test if your gloves are really waterproof! 🧤",
    "❄ Snowball fight, anyone? Choose your team wisely! 🎯",
    "❄ Hot chocolate season is officially in session! ☕",
    "❄ Time to show off those winter fashion layers! 🧣",
    "❄ Your car might need a snow blanket today! 🚗",
    "❄ Perfect day for indoor fort building! 🏰"
]

CLEAR_HOT_MESSAGES = [
    "☀ Sunglasses? Check. Sunscreen? Check. Summer vibes? Double check! 🕶",
    "☀ Hot enough to fry an egg on the sidewalk! (Please don't try) 🍳",
    "☀ Time to become best friends with your AC! 🌡",
    "☀ Beach day alert! Time to work on those sandcastle skills! 🏖",
    "☀ Perfect weather for ice cream... or two... or three! 🍦",
    "☀ Your plants might need an extra drink today! 🌿",
    "☀ Time to test if your sunscreen really is waterproof! 🏊‍♂",
    "☀ Perfect day for a rooftop party! Just bring extra water! 🎉",
    "☀ Warning: Hot weather may cause spontaneous pool parties! 💦",
    "☀ Time to show off those summer fashion choices! 👕"
]

CLEAR_MILD_MESSAGES = [
    "🌤 Perfect weather for everything! Literally everything! 🎯",
    "🌤 Mother Nature showing off her perfect weather skills! 🌈",
    "🌤 Time for that picnic you've been planning forever! 🧺",
    "🌤 Perfect day for outdoor yoga... or napping in the park! 🧘‍♀",
    "🌤 Weather so nice, even your phone wants to go outside! 📱",
    "🌤 Time to dust off that bicycle! 🚲",
    "🌤 Picture perfect weather for your social media feed! 📸",
    "🌤 Nature's way of saying 'go touch some grass'! 🌱",
    "🌤 Perfect weather for a spontaneous adventure! 🗺",
    "🌤 Time to write poetry under a tree! 📝"
]

CLOUDY_MESSAGES = [
    "☁ The clouds are playing hide and seek with the sun! 🎭",
    "☁ Fifty shades of grey... in the sky! 🎨",
    "☁ Perfect lighting for your moody photoshoot! 📸",
    "☁ The sun is just taking a quick nap behind the clouds! 😴",
    "☁ Cloud-watching day! That one looks like a dragon! 🐉",
    "☁ Nature's way of providing natural shade! ⛅",
    "☁ Time for some cloud appreciation! 🤍",
    "☁ Perfect weather for a mysterious movie scene! 🎬",
    "☁ The sky's version of a cozy blanket! 🛏",
    "☁ Clouds gathering for their daily meeting! 📊"
]


def get_rotating_message(message_list):
    """Get a random message from the list to ensure variety."""
    return random.choice(message_list)


def get_weather_alerts(city, current_temp, current_condition, weather_data):
    """Generate weather alerts based on temperature and historical data."""
    # Get historical temperature data for comparison - use seasonal
    historical_trends = get_temperature_trends(city, seasonal=True)

    alerts = []

    # Check if we have historical data to compare
    if historical_trends:
        # Calculate average historical temperature for this time of year
        avg_historical_temp = sum(float(trend[2]) for trend in historical_trends) / len(historical_trends)

        # Check for temperature anomalies (5°C difference as threshold)
        if current_temp > avg_historical_temp + 5:
            alerts.append(f"⚠ ALERT: Current temperature is unusually high for {city} this time of year!")
        elif current_temp < avg_historical_temp - 5:
            alerts.append(f"⚠ ALERT: Current temperature is unusually low for {city} this time of year!")

    # Check for severe weather conditions
    severe_conditions = ['thunderstorm', 'tornado', 'hurricane', 'blizzard', 'hail']
    for condition in severe_conditions:
        if condition in current_condition.lower():
            alerts.append(f"🚨 SEVERE WEATHER ALERT: {condition.capitalize()} detected in {city}!")

    # Add air quality alerts if available
    if 'air_quality_index' in weather_data and weather_data['air_quality_index'] >= 4:
        alerts.append(
            f"😷 AIR QUALITY ALERT: Poor air quality detected in {city}. Consider limiting outdoor activities.")

    return alerts


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
        .favorite-city {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            cursor: pointer;
            transition: background-color 0.3s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .favorite-city:hover {
            background-color: #e9ecef;
        }
        .city-name {
            flex-grow: 1;
            font-weight: 500;
        }
        .remove-btn {
            color: #dc3545;
            cursor: pointer;
            margin-left: 10px;
        }
        .limit-badge {
            background-color: #6c757d;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            margin-left: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'favorite_cities' not in st.session_state:
    st.session_state.favorite_cities = []
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False
if 'favorite_message' not in st.session_state:
    st.session_state.favorite_message = None

# Main title and description
st.title("🌤 WeatherWise Pro")
st.write("Your Smart Weather Companion - Now with Extra Fun! 🌍")

# Authentication in sidebar
with st.sidebar:
    st.header("👤 User Area")

    # Place tabs for login/register/account
    auth_tab1, auth_tab2, auth_tab3 = st.tabs(["Login", "Register", "Account"])

    # Login tab
    with auth_tab1:
        if not st.session_state.authenticated:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submit = st.form_submit_button("Login")

                if submit:
                    if username and password:
                        auth_success, user_info = authenticate(username, password)

                        if auth_success:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_id = user_info["id"]

                            # Make sure this username exists in our weather database too
                            weather_user = get_or_create_user(username)
                            if weather_user:
                                # Load favorite cities
                                st.session_state.favorite_cities = get_user_cities(weather_user['id'])

                            st.success(f"Welcome back, {username}! 🎉")
                            st.session_state.rerun = True
                        else:
                            st.error("Username/password is incorrect")
        else:
            st.success(f"Logged in as {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_id = None
                st.session_state.favorite_cities = []
                st.session_state.rerun = True

    # Register tab
    with auth_tab2:
        # Display registration success message if needed
        if st.session_state.registration_success:
            st.success("Registration successful! You can now login.")
            # Reset after showing
            st.session_state.registration_success = False

        if not st.session_state.authenticated:
            with st.form("register_form"):
                st.subheader("Create an Account")
                reg_username = st.text_input("Username", key="reg_username")
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_password_repeat = st.text_input("Repeat Password", type="password", key="reg_password_repeat")
                reg_email = st.text_input("Email", key="reg_email")

                submit = st.form_submit_button("Register")

                if submit:
                    if reg_password != reg_password_repeat:
                        st.error("Passwords do not match")
                    elif not reg_username or not reg_name or not reg_password or not reg_email:
                        st.error("Please fill in all fields")
                    else:
                        success, message = register_user(reg_username, reg_name, reg_password, reg_email)
                        if success:
                            # Create user in database
                            get_or_create_user(reg_username)
                            # Store success message in session state to display after rerun
                            st.session_state.registration_success = True
                            st.success("Registration successful! You can now login.")
                            st.session_state.rerun = True
                        else:
                            st.error(message)
        else:
            st.info("You are already registered and logged in.")

    # Account tab (only shown when logged in)
    with auth_tab3:
        if st.session_state.authenticated:
            user_info = get_user(st.session_state.username)

            st.subheader("Account Information")
            st.write(f"Username: {st.session_state.username}")
            st.write(f"Name: {user_info.get('name', '')}")
            st.write(f"Email: {user_info.get('email', '')}")

            with st.expander("Change Password"):
                with st.form("change_password_form"):
                    current_password = st.text_input("Current Password", type="password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm New Password", type="password")

                    submit = st.form_submit_button("Update Password")

                    if submit:
                        if new_password != confirm_password:
                            st.error("New passwords do not match")
                        else:
                            success, message = change_password(
                                st.session_state.username,
                                current_password,
                                new_password
                            )
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
        else:
            st.info("Please login to view account information")

    # Display favorite cities if logged in
    if st.session_state.authenticated:
        st.header("⭐ Favorite Cities")

        # Show the limit counter
        city_count = len(st.session_state.favorite_cities)
        st.markdown(f"<div>You have saved <b>{city_count}/10</b> cities</div>", unsafe_allow_html=True)

        # Show message if there's any
        if st.session_state.favorite_message:
            st.info(st.session_state.favorite_message)
            st.session_state.favorite_message = None

        if not st.session_state.favorite_cities:
            st.info("You haven't saved any favorite cities yet. Search for a city and add it to your favorites!")
        else:
            for city in st.session_state.favorite_cities:
                col1, col2 = st.columns([5, 1])

                with col1:
                    if st.button(f"🌆 {city}", key=f"fav_{city}"):
                        st.session_state.selected_city = city
                        st.session_state.rerun = True

                with col2:
                    if st.button("❌", key=f"remove_{city}"):
                        weather_user = get_or_create_user(st.session_state.username)
                        if remove_user_city(weather_user['id'], city):
                            st.session_state.favorite_cities.remove(city)
                            st.session_state.favorite_message = f"Removed {city} from favorites"
                            st.session_state.rerun = True

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

# CSS to ensure straight alignment
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

# Main weather display
# Get selected city from session state
selected_city = st.session_state.selected_city
if selected_city:
    weather_data = get_weather(selected_city)
    forecast_data = get_forecast(selected_city)

    # Add to favorites button (only for logged in users)
    if st.session_state.authenticated:
        weather_user = get_or_create_user(st.session_state.username)

        if selected_city not in st.session_state.favorite_cities:
            if st.button(f"⭐ Add {selected_city} to Favorites"):
                success, message = add_user_city(weather_user['id'], selected_city)
                if success and "already in favorites" not in message:
                    st.session_state.favorite_cities.append(selected_city)
                    st.success(f"Added {selected_city} to favorites!")
                    st.session_state.favorite_message = message
                    st.session_state.rerun = True
                else:
                    st.info(message)
        else:
            st.info(f"{selected_city} is already in your favorites")

    if "error" in weather_data:
        st.error(f"🚫 {weather_data['error']}")
    else:
        # Current Weather Display with better styling
        st.markdown("### Current Weather")
        cols = st.columns([1, 1, 1, 1])

        metrics = [
            ("Temperature", weather_data["temperature"], "🌡"),
            ("Humidity", weather_data["humidity"], "💧"),
            ("Wind Speed", weather_data["wind_speed"], "💨"),
            ("Condition", weather_data["condition"], "☁")
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

        # Generate and display weather alerts
        alerts = get_weather_alerts(selected_city, temp_value, weather_data["condition"], weather_data)

        # Display alerts if any exist
        if alerts:
            st.markdown("### ⚠ Weather Alerts")
            for alert in alerts:
                st.error(alert)

        # Test data button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Add Test Data", key="add_test_data"):
                if add_test_historical_data(selected_city, temp_value):
                    st.success("Test data added successfully!")
                else:
                    st.error("Failed to add test data")

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
                            {f"<div class='forecast-data'>💧 {day['humidity']}</div>" if 'humidity' in day else ""}
                            {f"<div class='forecast-data'>💨 {day['wind_speed']}</div>" if 'wind_speed' in day else ""}
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
        <p>Made with ❤ using Streamlit & SQLite</p>
    </div>
    """,
    unsafe_allow_html=True)