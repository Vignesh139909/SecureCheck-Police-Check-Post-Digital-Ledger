# 🚨 SecureCheck: Police Check Post Digital Ledger

**Real-time analytics and decision support for traffic enforcement.**

SecureCheck is a police data dashboard built using **Streamlit** and connected to a **MySQL database**. It helps law enforcement analyze and visualize daily traffic stop logs, run advanced analytics, and even predict outcomes and violations based on historical patterns.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Dashboard Explanation](#dashboard-explanation)
- [Advanced Analytics](#advanced-analytics)
- [Violation & Outcome Prediction](#violation--outcome-prediction)
- [Contributing](#contributing)

---

## Overview

**SecureCheck** is built to modernize how police post logs are viewed and analyzed. It provides an intuitive interface for filtering data, viewing metrics, analyzing demographic patterns, and deriving insights through rich interactive charts.

✅ Built with:
- **Python**
- **Streamlit**
- **MySQL**
- **Pandas & Plotly**
- **Lottie Animations**

---

## Features

- 📋 **Police Stop Logs**: View, filter, and export real stop records.
- 📊 **Interactive Analytics**: Analyze stop trends by gender, time, location, violation, etc.
- ⚙️ **Advanced Reports**: Visual deep-dives based on SQL queries.
- 🤖 **Violation & Outcome Prediction**: Smart form-based record matching to suggest likely outcomes.
- 📁 **CSV Export**: Download filtered datasets instantly.

---

## Install dependencies

  - pip install streamlit pandas mysql-connector-python plotly streamlit-lottie
---

## Set up the MySQL database
- Create a database named Securecheck_ledger.

## Import your dataset into a table named police_stops.

## Sample table schema expected:

vehicle_number, stop_date, stop_time, driver_gender, driver_age,
driver_race, violation, search_conducted, search_type,
drugs_related_stop, stop_outcome, stop_duration, is_arrested, country

---
Update the database connection section in Records.py:
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='Securecheck_ledger'
)
---
## Run the app
streamlit run Records.py
---
## Usage
Once running, visit http://localhost:8501 in your browser.

 ## 🔍 Filter & View Logs
- Select from date range, gender, country, drugs, arrests

- View filtered stop data

- Export to CSV

- Get summary statistics on stops, arrests, and drug involvement

## Dashboard Explanation

### 📊 Analytics & Reports Page

#### 🟡 Medium-Level Analysis

- **Vehicle-Based**: Most searched or flagged vehicles
- **Demographics**: Arrest/search rates by age, gender, race
- **Time Trends**: Stop patterns by hour, duration, day/night
- **Violation-Based**: Common violations, search/arrest association
- **Location-Based**: Drug stop rates, arrest frequency per country

#### 🔴 Complex Insights

- **Yearly Trends**: Country-wise yearly arrest progression
- **Race/Age Violation Patterns**
- **Hourly/Monthly Stop Distribution**
- **Top Violation Rankings**
- **Driver Profiles by Country**

---

## Violation & Outcome Prediction

### 🎯 Predictive Lookup Form

Enter values like:

- Vehicle Number
- Stop Date & Time
- Driver Info (Age, Gender, Race)
- Search Conducted
- Drugs Involved
- Stop Duration

🚀 Output:

- Predicted violation
- Predicted stop outcome
- Clear, human-readable summary

✅ Great for record retrieval or report simulation.

---

## Advanced Analytics

You can run advanced SQL-based insights such as:

- 🚔 Stop frequency by violation
- 👮 Arrest probability by age or time
- 🌍 Comparison of drug stops across countries
- ⏱️ Duration-based violation trends
- 🏅 Top violations by arrest rate

These insights are visualized using interactive Plotly charts.

---


