import os
from flask import Flask, render_template, request
import pandas as pd
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Ensure the 'static' directory exists
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

API_KEY = os.getenv("WEATHER_API_KEY", "H9G4MQB6VYXWHCWRSUWUZUCQN")  # Replace with your actual key

def fetch_weather(city):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    url = f"{base_url}/{city}/{start_date}/{end_date}?unitGroup=metric&include=days&key={API_KEY}&contentType=json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return [
            {
                "city": city,
                "date": entry["datetime"],
                "tempmax": entry.get("tempmax", "N/A"),
                "tempmin": entry.get("tempmin", "N/A"),
                "humidity": entry.get("humidity", "N/A"),
                "windspeed": entry.get("windspeed", "N/A")
            }
            for entry in data.get("days", [])
        ]
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {city}: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city_input = request.form.get("city", "").strip()
        if not city_input:
            return render_template("index.html", error="Please enter a city name.", weather_data=None)

        cities = [city.strip() for city in city_input.split(",")]
        all_weather_data = [weather for city in cities for weather in fetch_weather(city)]

        # Save to CSV only if data is present
        if all_weather_data:
            df = pd.DataFrame(all_weather_data)
            csv_path = os.path.join(STATIC_DIR, "weather_data.csv")
            df.to_csv(csv_path, index=False)

        return render_template("index.html", weather_data=all_weather_data, city_input=city_input)

    return render_template("index.html", weather_data=None)

if __name__ == "__main__":
    app.run(debug=True)
