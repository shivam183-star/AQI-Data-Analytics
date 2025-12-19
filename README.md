# Air Quality Index (AQI) Analysis using Python & OpenWeather API

## Overview
This project is a **Python-based AQI analysis tool** that fetches **real-time and historical air pollution data** for any city using the **OpenWeather Air Pollution API**.

It calculates AQI based on **Indian AQI standards**, visualizes pollutant concentrations, and displays **year-wise AQI trends**.

---

## Features
- City-based AQI analysis
- Pollutant concentration bar graph (PM2.5, PM10, CO, NO₂, SO₂, O₃)
- Historical AQI trend analysis (year-wise)
- AQI calculation using **Indian AQI standards**
- Secure API key handling with `.env`
- Menu-driven interactive CLI

---

## Tech Stack
- **Python**
- **OpenWeather Air Pollution API**
- `requests`
- `pandas`
- `matplotlib`
- `python-dotenv`

---

## Project Structure
```
AQI-Analysis-Python/
│── main.py
│── requirements.txt
│── .gitignore
│── README.md
│── .env   (not pushed to GitHub)
```

---

## Setup Instructions

### 1️. Clone the repository
```bash
git clone https://github.com/shivam183-star/AQI-Data-Analytics.git
cd AQI-Data-Analytics
```

### 2️. Install dependencies
```bash
pip install -r requirements.txt
```

### 3️. Create `.env` file
Create a file named `.env` in the project root:
```
API_KEY=your_openweather_api_key_here
```
> Never share or push your API key to GitHub

---

## Run the Project
```bash
python main.py
```

---

## Program Options
After entering the city name:
```
1. Show AQI
2. Show pollutant concentrations
3. Show historical AQI data
4. Exit
```

---

## AQI Categories (Indian Standard)

| AQI Range | Category |
|---------|----------|
| 0–50 | Good |
| 51–100 | Satisfactory |
| 101–200 | Moderate |
| 201–300 | Poor |
| 301–400 | Very Poor |
| 401+ | Severe |

---

## AQI Calculation Logic
- AQI is calculated using **PM2.5** and **PM10** concentrations
- Final AQI = **max(AQI_PM2.5, AQI_PM10)**
- Breakpoints follow **Indian AQI guidelines**

---

## API Used
**OpenWeather Air Pollution API**
- Real-time air quality data
- Historical air quality data

---

## Output
- Bar chart for pollutant concentrations
- Line graph for yearly average AQI trend

---

## Use Cases
- Environmental data analysis
- College mini/major projects
- Internship & resume projects
- AQI trend visualization

---

## Future Improvements
- Streamlit-based web dashboard
- Export AQI data to CSV
- City-to-city AQI comparison
- API call optimization with caching

---

## Author
**Shivam**
- Student | Python Learner
- @shivam183-star

---

## Support
If you find this project useful, consider giving it a star on GitHub!

