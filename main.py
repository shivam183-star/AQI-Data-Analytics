import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

city = input("Enter City: ").lower()

geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
response = requests.get(geo_url)

geo_data = response.json()

lat = geo_data[0]["lat"]
lon = geo_data[0]["lon"]

air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
air_data = requests.get(air_url).json()

# print(air_data)

components = air_data["list"][0]["components"]
aqi_index = air_data["list"][0]["main"]["aqi"]

df = pd.DataFrame([components])
df["AQI_Index"] = aqi_index
df["City"] = city

def year_to_unix_range(year):
    start = int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp())
    return start, end

def ShowAQI(city):
    AQI = Standard_AQI(df.loc[0, "pm2_5"], df.loc[0, "pm10"])
    print(f"AQI in {city} is", AQI)
    print(f"Air Quality in {city} is", aqi_category(AQI))


def ShowConc(city):
    pollutants = ["pm2_5", "pm10", "co", "no2", "so2", "o3"]

    plt.figure(figsize=(10,5))
    plt.bar(pollutants, df[pollutants].iloc[0], color ="#7bdef9", edgecolor ="black")
    plt.xlabel("Pollutants", fontsize=14, weight="bold", fontname="Times New Roman", color="#333333")
    plt.ylabel("Concentration (µg/m³)", fontsize=14, weight="bold", fontname="Times New Roman", color="#333333")
    plt.title(f"Air Pollutants concentrations in {city}", fontsize=16, weight="bold", fontname="Times New Roman", color="#B10E34")
    plt.show()


def History(city):
    start_year = int(input(f"AQI history in {city} since year: "))
    records = []
    current_year = datetime.now().year

    for year in range(start_year, current_year+1):
        start_unix, end_unix = year_to_unix_range(year)

        print(f"Fetching AQI data for {year}...")

        history_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution/history"
            f"?lat={lat}&lon={lon}&start={start_unix}&end={end_unix}"
            f"&appid={API_KEY}"
        )

        response = requests.get(history_url).json()

        if "list" not in response:
            print(f"No data available for {year}")
            continue

        for item in response["list"]:
            records.append({
                "year": year,
                "aqi": Standard_AQI(item["components"]["pm2_5"], item["components"]["pm10"])
            })

        time.sleep(0.5)

    df = pd.DataFrame(records)

    if df.empty:
        print("No AQI data fetched. Check API limits.")

    yearly_avg = df.groupby("year")["aqi"].mean().reset_index()

    print("\nYearly Average AQI:")
    print(yearly_avg)

    plt.figure(figsize=(10, 5))
    plt.plot(yearly_avg["year"], yearly_avg["aqi"], marker="o", color="#FF5733")

    plt.xlabel("Year", fontsize=14, weight="bold", fontname="Times New Roman", color="#333333")
    plt.ylabel("Average AQI ", fontsize=14, weight="bold", fontname="Times New Roman", color="#333333")
    plt.title(f"Yearly Average AQI Trend in {city}", fontsize=16, weight="bold", fontname="Times New Roman", color="#B10E34")
    plt.xticks(yearly_avg["year"])
    plt.grid(True)

    plt.show()

def pm25_aqi(pm):
    if pm <= 30:
        return round((pm / 30) * 50)
    elif pm <= 60:
        return round(51 + (pm - 31) * (49 / 29))
    elif pm <= 90:
        return round(101 + (pm - 61) * (99 / 29))
    elif pm <= 120:
        return round(201 + (pm - 91) * (99 / 29))
    elif pm <= 250:
        return round(301 + (pm - 121) * (99 / 129))
    else:
        return round(401 + (pm - 251) * (99 / 249))


def pm10_aqi(pm):
    if pm <= 50:
        return round(pm)
    elif pm <= 100:
        return round(51 + (pm - 51))
    elif pm <= 250:
        return round(101 + (pm - 101) * (99 / 149))
    elif pm <= 350:
        return round(201 + (pm - 251))
    elif pm <= 430:
        return round(301 + (pm - 351) * (99 / 79))
    else:
        return round(401 + (pm - 431) * (99 / 169))


def Standard_AQI(pm25, pm10):
    aqi_pm25 = pm25_aqi(pm25)
    aqi_pm10 = pm10_aqi(pm10)

    final_aqi = max(aqi_pm25, aqi_pm10)

    return final_aqi

def aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"
    
print(f"""Select any option
1. Show AQI in {city}
2. Show pollutant concentrations
3. Show Historical Data of AQI in {city}
4. Exit""")

while True:
    choice = int(input("Enter an option: "))

    if choice == 1:
        ShowAQI(city)
    elif choice == 2:
        ShowConc(city)
    elif choice == 3:
        History(city)
    elif choice == 4:
        exit()
    else:
        print("Invalid choice")


