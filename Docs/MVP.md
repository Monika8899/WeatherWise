# Weather Wise App - MVP

## Overview

Our goal is to develop a basic but fully functional weather application within 2-4 weeks.

---

## MVP Features

1. **Current Weather & Short Forecast**
   - **What**: Display current weather (temperature, humidity, wind speed, conditions) for a user-specified city.
   - **Why**: Provides immediate, practical information to help the user plan their day.
   - **Scope**: Include a 3-day forecast (daily high, low, and general condition).

2. **Multi-City Support (Basic)**
   - **What**: Store multiple city entries so users can switch among various locations.
   - **Why**: Allows quick weather checks for different places (home, travel destinations, etc.).
   - **Scope**: Simple data storage (e.g., SQLite or JSON) to save and retrieve city names.

3. **Minimal Interface**
   - **What**: Provide a clear, simple UI or CLI with essential weather data.
   - **Why**: Ensures quick understanding for the user; no unnecessary complexity.
   - **Scope**: Basic text-based menu (CLI) or a simple Flask/Django webpage with one or two routes.

4. **Free Weather API Integration**
   - **What**: Use a free tier API (e.g., OpenWeatherMap) to fetch weather data.
   - **Why**: Keeps costs at zero and limits complexity to available free endpoints.
   - **Scope**: Basic GET requests, error handling for invalid city or connection issues.

5. **Error Handling**
   - **What**: Show user-friendly error messages if the API fails or city name is invalid.
   - **Why**: Improves user experience by clarifying issues instead of crashing.
   - **Scope**: Basic try-except blocks, checks for HTTP errors, user notification.

---

## Out of Scope (Not in MVP)
- Hourly breakdown or extended (7+ day) forecasts
- Notifications or weather alerts
- Historical weather or data analytics
- Complex user profiles or authentication
- Social media or calendar integrations
- Offline mode / caching
- Theming or customization options
- Air Quality Index or health recommendations
- GPS-based location detection

---

## Technology & Approach
- **Language**: Python
- **Data Storage**: SQLite or a simple JSON file
- **API**: Free tier of OpenWeatherMap (or a similar free weather API)
- **UI**:
  - Option A: Command Line Interface (CLI)
  - Option B: Minimal Flask/Django web page

