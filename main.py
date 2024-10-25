import requests
import tkinter
import time
import sqlite3
from datetime import datetime
import cred
import matplotlib.pyplot as plt

# Configuration
API_KEY = cred.keyID  
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
UPDATE_INTERVAL = 300  # Update interval in seconds (5 minutes)
THRESHOLD_TEMP_CELSIUS = 35  # Celsius threshold for alerts

# Database setup
def setup_database():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    city TEXT,
                    avg_temp REAL,
                    max_temp REAL,
                    min_temp REAL,
                    dominant_condition TEXT)''')
    conn.commit()
    return conn

# Function to convert temperature from Kelvin to Celsius or Fahrenheit
def convert_temperature(kelvin_temp, unit='Celsius'):
    if unit == 'Celsius':
        return int(kelvin_temp - 273.15)
    elif unit == 'Fahrenheit':
        return int((kelvin_temp - 273.15) * 9/5 + 32)
    return kelvin_temp  # Return Kelvin if unit is unknown

# Fetch weather data from OpenWeatherMap API
def fetch_weather():
    weather_data = []
    for i, cityname in enumerate(CITIES):
        api = f'https://api.openweathermap.org/data/2.5/weather?q={cityname}&appid={API_KEY}'
        data = requests.get(api).json()

        if data.get('cod') != 200:  
            print(f"Error fetching data for {cityname}: {data.get('message', 'Unknown error')}")
            continue

        kelvin_temp = data['main']['temp']
        feels_like_kelvin = data['main']['feels_like']
        max_temp_kelvin = data['main']['temp_max']
        min_temp_kelvin = data['main']['temp_min']
        
        # Convert temperatures based on user preference
        temperature = convert_temperature(kelvin_temp, unit_var.get())
        feels_like = convert_temperature(feels_like_kelvin, unit_var.get())
        maxTemp = convert_temperature(max_temp_kelvin, unit_var.get())
        minTemp = convert_temperature(min_temp_kelvin, unit_var.get())
        
        weathercondition = data['weather'][0]['main']
        weatherdescription = str(data['weather'][0]['description'])
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        windSpeed = data['wind']['speed']
        sunrise = time.strftime('%I:%M:%S', time.gmtime(data['sys']['sunrise'] - 21600))
        sunset = time.strftime('%I:%M:%S', time.gmtime(data['sys']['sunset'] - 21600))

        # Update the city frame with weather data
        city_frame = city_frames[i]
        city_frame.info_label.config(text=f"{cityname}: {weathercondition}\n{temperature}°{unit_var.get()[0]}\nFeels Like: {feels_like}°{unit_var.get()[0]}")
        city_frame.data_label.config(text=(f"\nDESCRIPTION: {weatherdescription}\n"
                                            f"FEELS LIKE: {feels_like}°{unit_var.get()[0]}\n"
                                            f"MAX TEMP: {maxTemp}°{unit_var.get()[0]}\n"
                                            f"MIN TEMP: {minTemp}°{unit_var.get()[0]}\n"
                                            f"AVG TEMP: {temperature}°{unit_var.get()[0]}\n"
                                            f"HUMIDITY: {humidity}%\n"
                                            f"PRESSURE: {pressure} hPa\n"
                                            f"WIND SPEED: {windSpeed} km/h\n"
                                            f"SUNRISE: {sunrise}\n"
                                            f"SUNSET: {sunset}\n"
                                            f"DATE: {datetime.now().strftime('%Y-%m-%d')}\n"
                                            f"TIME: {datetime.now().strftime('%H:%M:%S')}"))

        # Fetch and display the weather icon
        weatherIcon = data['weather'][0]['icon']
        FetchIcon(city_frame.icon_label, weatherIcon)

        # Collect data for daily summary
        weather_data.append({
            'city': cityname,
            'main': weathercondition,
            'temp': temperature,
            'max_temp': maxTemp,
            'min_temp': minTemp,
            'feels_like': feels_like,
            'dt': datetime.now().date()
        })

        time.sleep(1)  # To avoid hitting the API too fast

    calculate_daily_summary(weather_data)
    check_alerts(weather_data)

    frame.after(UPDATE_INTERVAL * 1000, fetch_weather)

# Function to save daily summaries to the database
def save_daily_summary(conn, date, city, avg_temp, max_temp, min_temp, dominant_condition):
    c = conn.cursor()
    c.execute('INSERT INTO daily_summary (date, city, avg_temp, max_temp, min_temp, dominant_condition) VALUES (?, ?, ?, ?, ?, ?)', 
              (date, city, avg_temp, max_temp, min_temp, dominant_condition))
    conn.commit()

# Calculate daily summary and store it in the database
def calculate_daily_summary(weather_data):
    daily_summary = {}
    
    for entry in weather_data:
        city = entry['city']
        date = entry['dt']
        temp = entry['temp']
        
        if (city, date) not in daily_summary:
            daily_summary[(city, date)] = {
                'temps': [],
                'max_temp': float('-inf'),
                'min_temp': float('inf'),
                'conditions': {}
            }
        
        daily_summary[(city, date)]['temps'].append(temp)
        daily_summary[(city, date)]['max_temp'] = max(daily_summary[(city, date)]['max_temp'], temp)
        daily_summary[(city, date)]['min_temp'] = min(daily_summary[(city, date)]['min_temp'], temp)
        
        if entry['main'] not in daily_summary[(city, date)]['conditions']:
            daily_summary[(city, date)]['conditions'][entry['main']] = 0
        daily_summary[(city, date)]['conditions'][entry['main']] += 1
    
    for (city, date), summary in daily_summary.items():
        avg_temp = sum(summary['temps']) / len(summary['temps']) if summary['temps'] else 0
        dominant_condition = max(summary['conditions'], key=summary['conditions'].get, default="N/A")
        save_daily_summary(conn, str(date), city, avg_temp, summary['max_temp'], summary['min_temp'], dominant_condition)

# Check for alert conditions
def check_alerts(weather_data):
    for entry in weather_data:
        if entry['temp'] > THRESHOLD_TEMP_CELSIUS:
            print(f"Alert! {entry['city']} has exceeded the temperature threshold: {entry['temp']}°{unit_var.get()[0]}")

# To fetch the ICON field from the API
def FetchIcon(icon_label, icon_code):
    iconUrl = f"http://openweathermap.org/img/w/{icon_code}.png"
    iconResponse = requests.get(iconUrl)
    iconImage = tkinter.PhotoImage(data=iconResponse.content)
    icon_label.configure(image=iconImage)
    icon_label.image = iconImage  

# Function to plot daily weather summaries
def plot_daily_summaries():
    c = conn.cursor()
    for city in CITIES:
        c.execute('SELECT date, avg_temp FROM daily_summary WHERE city=? ORDER BY date', (city,))
        rows = c.fetchall()
        
        dates = [row[0] for row in rows]
        avg_temps = [row[1] for row in rows]
        
        plt.plot(dates, avg_temps, label=city)

    plt.title('Average Daily Temperature')
    plt.xlabel('Date')
    plt.ylabel('Average Temperature (°C)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to plot triggered alerts
def plot_alerts():
    alert_data = {}
    c = conn.cursor()
    for city in CITIES:
        c.execute('SELECT date, avg_temp FROM daily_summary WHERE city=? AND avg_temp > ?', (city, THRESHOLD_TEMP_CELSIUS))
        rows = c.fetchall()
        alert_data[city] = len(rows)
    
    plt.bar(alert_data.keys(), alert_data.values(), color='orange')
    plt.title('Triggered Alerts for Temperature Exceedance')
    plt.xlabel('City')
    plt.ylabel('Number of Alerts')
    plt.tight_layout()
    plt.show()

# Function to toggle full screen
def toggle_fullscreen():
    global fullscreen
    fullscreen = not fullscreen
    frame.attributes('-fullscreen', fullscreen)

# Function to exit the application
def close_application():
    frame.quit()

# For Application Window Size
frame = tkinter.Tk()
fullscreen = True
frame.geometry('1200x500')   # Open in full screen
frame.title('WEATHER CASTER')
frame.configure(bg='light blue')

# # Button to toggle full screen with text
# fullscreen_button = tkinter.Button(frame, text="Toggle Full Screen", command=toggle_fullscreen, bg='light blue', borderwidth=0)
# fullscreen_button.pack(side='top', anchor='ne', padx=10, pady=10)  # Position at the top right

# Frame for control buttons
control_frame = tkinter.Frame(frame, bg='light blue')
control_frame.pack(side='top', anchor='ne', padx=10, pady=40)  # Position below the fullscreen button

# Dropdown for temperature unit selection
unit_var = tkinter.StringVar(value='Celsius')
unit_dropdown = tkinter.OptionMenu(control_frame, unit_var, 'Celsius', 'Fahrenheit', command=lambda _: fetch_weather())
unit_dropdown.pack(side='left', padx=5)

# Button to plot daily summaries
summary_button = tkinter.Button(control_frame, text="Daily Summaries", command=plot_daily_summaries)
summary_button.pack(side='left', padx=5)

# Button to plot triggered alerts
alerts_button = tkinter.Button(control_frame, text="Show Alerts", command=plot_alerts)
alerts_button.pack(side='left', padx=5)

# Close button positioned in the top right corner
close_button = tkinter.Button(control_frame, text="Close", command=close_application)
close_button.pack(side='left', padx=5)

# Setup database
conn = setup_database()

# Create a list to hold city frames
city_frames = []

# Create frames for each city
for city in CITIES:
    city_frame = tkinter.Frame(frame, bg='light blue', bd=2, relief='ridge')
    city_frame.pack(side='left', padx=5, pady=5)

    city_frame.icon_label = tkinter.Label(city_frame, bg='light blue')
    city_frame.icon_label.pack()

    city_frame.info_label = tkinter.Label(city_frame, font=('Eras Bold ITC', 14), bg='light blue')
    city_frame.info_label.pack()

    city_frame.data_label = tkinter.Label(city_frame, font=('Eras Bold ITC', 10), bg='light blue')
    city_frame.data_label.pack()

    city_frames.append(city_frame)

# Start fetching weather data
fetch_weather()

# To make frame visible
frame.mainloop()

# Close database connection on exit
conn.close()
