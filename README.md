# WEATHER MONITOR

Weather Monitor is a Python application that provides real-time weather data for major cities in India. It utilizes the OpenWeatherMap API to display current weather conditions, temperature statistics, and daily summaries.

## Features
* Real-Time Weather Data: Fetches and displays current weather including Avg, Min, Max temperatures and other weather parameters(humidity, windspeed, sunset and sunrise) for multiple cities.
* Temperature Conversion: Supports Celsius and Fahrenheit.
* Daily Summaries: Saves daily temperature data to a SQLite database.
* Alerts: Notifies when temperatures exceed a defined threshold.
* Data Visualization: Uses Matplotlib to plot daily average temperatures and alert statistics.
* User-Friendly Interface: Built with Tkinter for an intuitive GUI experience.
  
## Technologies Used
* Python: The primary programming language used to develop the application.
* Tkinter: A standard GUI library for Python, used for creating the graphical user interface.
* SQLite: A lightweight database used to store daily weather summaries.
* Matplotlib: A plotting library for creating visualizations of temperature data and alerts.
* OpenWeatherMap API: Provides real-time weather data for cities worldwide.

## Setup
1. Clone the repository:
   ```bash
   https://github.com/Shruti1609/Weather_forecast.git

2. Install the required dependencies:
   ```bash
   pip install flask sqlalchemy requests matplotlib

* Create a cred.py file in the root directory and add your OpenWeatherMap API key:
  keyID = 'YOUR_API_KEY_HERE'

## Usage
1. Run the application:
   ```bash
   python weather_caster.py

* Use the dropdown to select the temperature unit (Celsius or Fahrenheit).

* View the current weather conditions and statistics for each city.

* Click the buttons to visualize daily summaries and alert statistics.

## Previews

### Database
![db_ss](https://github.com/user-attachments/assets/43907798-18d0-4045-a493-5960c0134748)

### Weather Monitor
<img width="847" alt="weather_monitor_ss" src="https://github.com/user-attachments/assets/d028b253-66ad-4c70-994e-56e2179f3569">


