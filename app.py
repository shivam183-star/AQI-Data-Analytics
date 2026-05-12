import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import time
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="AQI Dashboard",
    page_icon="🌍",
    layout="wide"
)

load_dotenv()
API_KEY = os.getenv("API_KEY")

st.markdown(
    """
    <style>
        .main {
            background-color: #0e1117;
        }

        .stMetric {
            border-radius: 15px;
            padding: 10px;
            background-color: #1c1f26;
        }

        .aqi-card {
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if not API_KEY:
    st.error("API_KEY not found in .env file")
    st.stop()

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


def standard_aqi(pm25, pm10):
    return max(pm25_aqi(pm25), pm10_aqi(pm10))


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
    return "Severe"


def aqi_color(aqi):
    if aqi <= 50:
        return "#2ecc71"
    elif aqi <= 100:
        return "#a3e635"
    elif aqi <= 200:
        return "#facc15"
    elif aqi <= 300:
        return "#fb923c"
    elif aqi <= 400:
        return "#ef4444"
    return "#7f1d1d"


def get_coordinates(city):
    geo_url = (
        f"http://api.openweathermap.org/geo/1.0/direct?"
        f"q={city}&limit=1&appid={API_KEY}"
    )

    try:
        response = requests.get(geo_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        return {
            "lat": data[0]["lat"],
            "lon": data[0]["lon"],
            "name": data[0]["name"],
            "country": data[0].get("country", "")
        }

    except requests.exceptions.RequestException:
        return None


@st.cache_data(ttl=600)
def get_air_pollution(lat, lon):
    air_url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={lat}&lon={lon}&appid={API_KEY}"
    )

    response = requests.get(air_url, timeout=10)
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=3600)
def get_historical_data(lat, lon, start_year, end_year):
    records = []

    progress_bar = st.progress(0)
    status = st.empty()

    total_years = end_year - start_year + 1

    for index, year in enumerate(range(start_year, end_year + 1)):
        status.write(f"Fetching data for {year}...")

        start_unix = int(
            datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()
        )

        end_unix = int(
            datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp()
        )

        history_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution/history"
            f"?lat={lat}&lon={lon}"
            f"&start={start_unix}"
            f"&end={end_unix}"
            f"&appid={API_KEY}"
        )

        try:
            response = requests.get(history_url, timeout=20)
            response.raise_for_status()
            history_data = response.json()

            if "list" not in history_data:
                continue

            sample_data = history_data["list"][::24]

            for item in sample_data:
                pm25 = item["components"].get("pm2_5", 0)
                pm10 = item["components"].get("pm10", 0)

                records.append(
                    {
                        "year": year,
                        "aqi": standard_aqi(pm25, pm10)
                    }
                )

        except requests.exceptions.RequestException:
            continue

        progress_bar.progress((index + 1) / total_years)
        time.sleep(0.2)

    status.empty()
    progress_bar.empty()

    return pd.DataFrame(records)


st.title("🌍 Air Quality Index Dashboard")
st.markdown(
    "Track AQI levels, pollutant concentrations, and historical air quality trends."
)

st.sidebar.header("🔎 Search City")
city = st.sidebar.text_input("Enter City Name", placeholder="Delhi")

show_history = st.sidebar.checkbox("Show Historical AQI")

current_year = datetime.now().year

if show_history:
    start_year = st.sidebar.slider(
        "Select Start Year",
        min_value=2013,
        max_value=current_year,
        value=current_year - 3
    )


if city:
    location = get_coordinates(city)

    if location is None:
        st.error("City not found or API request failed.")
        st.stop()

    lat = location["lat"]
    lon = location["lon"]

    try:
        air_data = get_air_pollution(lat, lon)

        components = air_data["list"][0]["components"]

        pm25 = components.get("pm2_5", 0)
        pm10 = components.get("pm10", 0)

        final_aqi = standard_aqi(pm25, pm10)
        category = aqi_category(final_aqi)
        color = aqi_color(final_aqi)

        df = pd.DataFrame([components])


        st.markdown(
            f"""
            <div class='aqi-card' style='background-color:{color}'>
                AQI in {location['name']}, {location['country']}<br><br>
                {final_aqi} - {category}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("PM2.5", f"{pm25} µg/m³")

        with col2:
            st.metric("PM10", f"{pm10} µg/m³")

        with col3:
            st.metric("CO", f"{components.get('co', 0)} µg/m³")

        with col4:
            st.metric("NO₂", f"{components.get('no2', 0)} µg/m³")

        st.write("")

        
        st.subheader("📊 Pollutant Concentrations")

        pollutants = ["pm2_5", "pm10", "co", "no2", "so2", "o3"]

        pollutant_df = pd.DataFrame(
            {
                "Pollutant": pollutants,
                "Concentration": [
                    components.get(pollutant, 0)
                    for pollutant in pollutants
                ]
            }
        )

        fig = px.bar(
            pollutant_df,
            x="Pollutant",
            y="Concentration",
            text_auto=True,
            title="Air Pollutant Concentrations"
        )

        fig.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(fig, width='stretch')


        st.subheader("📋 Detailed Pollutant Data")

        display_df = pollutant_df.copy()
        display_df.columns = ["Pollutant", "Concentration (µg/m³)"]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        
        if show_history:
            st.subheader("📈 Historical AQI Trend")

            history_df = get_historical_data(
                lat,
                lon,
                start_year,
                current_year
            )

            if history_df.empty:
                st.warning("No historical data available.")
            else:
                yearly_avg = (
                    history_df.groupby("year")["aqi"]
                    .mean()
                    .reset_index()
                )

                line_fig = go.Figure()

                line_fig.add_trace(
                    go.Scatter(
                        x=yearly_avg["year"],
                        y=yearly_avg["aqi"],
                        mode="lines+markers",
                        name="AQI"
                    )
                )

                line_fig.update_layout(
                    title=f"Yearly Average AQI Trend in {location['name']}",
                    xaxis_title="Year",
                    yaxis_title="Average AQI",
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(line_fig, width='stretch')

                st.subheader("📄 Yearly AQI Data")

                yearly_avg.columns = ["Year", "Average AQI"]

                st.dataframe(
                    yearly_avg,
                    use_container_width=True,
                    hide_index=True
                )

                csv = yearly_avg.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="⬇ Download AQI Data",
                    data=csv,
                    file_name=f"{city}_aqi_history.csv",
                    mime="text/csv"
                )

    except requests.exceptions.RequestException as e:
        st.error(f"API Request Failed: {e}")

    except Exception as e:
        st.error(f"Unexpected Error: {e}")


st.markdown("---")
st.caption("Built using Streamlit, Plotly, Pandas, and OpenWeatherMap API")
