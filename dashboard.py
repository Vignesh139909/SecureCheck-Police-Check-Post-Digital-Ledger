import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import datetime
from sqlalchemy import create_engine
from streamlit_lottie import st_lottie
import requests

def connect_to_database():
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='Securecheck_ledger'
        )
        return mydb
    except mysql.connector.Error as err:
        st.error(f"❌ DB Connection Error: {err}")
        return None

def fetch_data(query):
    db = connect_to_database()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)
            return df
        finally:
            db.close()
    else:
        return pd.DataFrame()

st.set_page_config(page_title="SecureCheck", page_icon="👮", layout="wide",initial_sidebar_state="collapsed")


page = st.sidebar.selectbox("Select Page", ["Data Records", "Analytics & Reports"])

st.markdown("""
    <style>
        html, body, [class*="st-"], .stApp {
            color: darkblue!important;
        }

    [data-testid="stAppViewContainer"] {
        background-image: url("https://i.ibb.co/k62fBtFf/Lowering-the-opacity.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
    }
    
    </style>
""", unsafe_allow_html=True)

st.title("👮 SecureCheck: Police Post Digital Ledger")

if page == "Data Records":
    st.sidebar.header("Filter Options")
    

    start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
    end_date = st.sidebar.date_input("End Date", pd.to_datetime("2030-12-30"))

    gender_filter = st.sidebar.radio("Driver Gender", ["All", "Male", "Female"])
    country_filter = st.sidebar.multiselect("Country", ["India", "USA", "Canada"], default=["India", "USA", "Canada"])
    drug_filter = st.sidebar.selectbox("Drug-Related Stop?", ["All", True, False])
    arrest_filter = st.sidebar.checkbox("Show Only Arrests", value=False)


    query = "SELECT * FROM police_stops"
    df = fetch_data(query)

    st.success(f"Total records : {len(df)}")
    st.header("🗃️ View & Filter Records")
    

    if not df.empty:
        df['stop_date'] = pd.to_datetime(df['stop_date'])

        filtered_df = df[(df['stop_date'] >= pd.to_datetime(start_date)) &(df['stop_date'] <= pd.to_datetime(end_date))]

        if gender_filter != "All":
            filtered_df = filtered_df[filtered_df['driver_gender'] == gender_filter]

        filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]   

        if drug_filter != "All":
            filtered_df = filtered_df[filtered_df['drugs_related_stop'] == drug_filter]

        if arrest_filter:
            filtered_df = filtered_df[filtered_df['is_arrested'] == True]

        
        st.dataframe(filtered_df, use_container_width=True)
        st.warning(f"Filtered Records: {len(filtered_df)}")

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Filtered Data", data=csv, file_name="filtered_data.csv", mime="text/csv")


        st.subheader("📊 Summary Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)

        
        col1.metric("🚦 Total Stops", len(filtered_df))
        gender_counts = filtered_df['driver_gender'].value_counts()
        male_count = gender_counts.get("Male", 0)
        female_count = gender_counts.get("Female", 0)
        col2.metric("👨 Male Drivers", male_count)
        col3.metric("👩 Female Drivers", female_count)
        col4.metric("🚨 Arrests", filtered_df['is_arrested'].sum())
        col5.metric("💊 Drug-Related Stops", filtered_df['drugs_related_stop'].sum())
    else:
        st.warning("No data available from the database.")

elif page == "Analytics & Reports":
    st.header("📊 Advanced Insights")
    st.sidebar.header("Analysis")
    analysis_section = st.sidebar.selectbox("📊 Select Analysis Type", [
        "🟡 Medium level", "🔴 Complex", "📝 New Entry + Prediction"
    ])

    if analysis_section == "🟡 Medium level":
        section = st.sidebar.radio("🧭 Select Category", [
            "🚗 Vehicle-Based",
            "🧍 Demographic-Based",
            "🕒 Time & Duration Based",
            "⚖️ Violation-Based",
            "🌍 Location-Based"
        ])
        def load_lottieurl(url):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_animation = load_lottieurl("https://lottie.host/dbb1df14-bbdc-4860-8e69-0155324ed160/RPTayiD5GJ.json")

        with st.sidebar:
            st_lottie(lottie_animation, speed=1, width=250, height=300, key="welcome_anim")

        st.subheader("🟡 Medium Level Analysis")

        if section == "🚗 Vehicle-Based":
            query_option = st.selectbox("Choose an Analysis", [
                "🚗 Top 10 vehicles involved in drug-related stops",
                "🚗 Most frequently searched vehicles"
            ])
            run_query = st.button("▶️ Run Query")


            if run_query:
                if query_option == "🚗 Top 10 vehicles involved in drug-related stops":
                    sql = """SELECT vehicle_number, COUNT(*) as stops
                    FROM police_stops 
                    WHERE drugs_related_stop = TRUE 
                    GROUP BY vehicle_number
                    ORDER BY stops DESC 
                    LIMIT 10"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="stops",y="vehicle_number",orientation="h",title="🚗 Top 10 Vehicles in Drug-Related Stops")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🚗 Most frequently searched vehicles":
                    sql = """SELECT vehicle_number, COUNT(*) as searches 
                    FROM police_stops 
                    WHERE search_conducted = TRUE 
                    GROUP BY vehicle_number
                    ORDER BY searches DESC
                    LIMIT 10"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="searches",y="vehicle_number",orientation="h",title="🚗 Most Frequently Searched Vehicles")
                    st.plotly_chart(fig, use_container_width=True)

        elif section == "🧍 Demographic-Based":
            query_option = st.selectbox("Choose an Analysis", [
                "🧍 Driver age group with highest arrest rate",
                "🧍 Gender distribution of drivers stopped in each country",
                "🧍 Race & gender combination with highest search rate"
            ])
            run_query = st.button("▶️ Run Query")


            if run_query:

                if query_option == "🧍 Driver age group with highest arrest rate":
                    sql =""" SELECT 
                    CASE
                        WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
                        WHEN driver_age BETWEEN 26 AND 35 THEN '26-35'
                        WHEN driver_age BETWEEN 36 AND 45 THEN '36-45'
                        WHEN driver_age BETWEEN 46 AND 60 THEN '46-60'
                        ELSE '60+'
                    END AS age_group,
                    AVG(is_arrested)*100 aS arrest_rate
                    FROM police_stops
                    GROUP BY age_group
                    ORDER BY arrest_rate DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="age_group",y="arrest_rate",color="age_group",title="🧍 Arrest Rate by Driver Age (%)")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🧍 Gender distribution of drivers stopped in each country":
                    sql = """SELECT country, driver_gender, COUNT(*) as total 
                    FROM police_stops 
                    GROUP BY country, driver_gender"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="country",y="total",color="driver_gender",barmode="group",title="🧍 Gender Distribution by Country")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🧍 Race & gender combination with highest search rate":
                    sql = """SELECT driver_race, driver_gender, AVG(search_conducted)*100 as search_rate 
                    FROM police_stops 
                    GROUP BY driver_race, driver_gender
                    ORDER BY search_rate DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="search_rate",y="driver_race",color="driver_gender",orientation="h",title="🧍 Race & Gender Search Rates (%)")
                    st.plotly_chart(fig, use_container_width=True)

        elif section == "🕒 Time & Duration Based":
            query_option = st.selectbox("Choose an Analysis", [
                "🕒 Time of day with most traffic stops",
                "🕒 Average stop duration for different violations",
                "🕒 Are night stops more likely to lead to arrests?"
            ])
            run_query = st.button("▶️ Run Query")


            if run_query:

                if query_option == "🕒 Time of day with most traffic stops":
                    sql = """SELECT HOUR(stop_time) as hour, COUNT(*) as total 
                    FROM police_stops 
                    GROUP BY hour ORDER BY hour"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="hour",y="total",title="🕒 Stops by Hour of Day")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🕒 Average stop duration for different violations":
                    sql = """SELECT violation,ROUND(AVG(
                    CASE stop_duration
                        WHEN '0-15 min' THEN 7.5
                        WHEN '16-30 min' THEN 23
                        WHEN '30+ min' THEN 35
                        ELSE 0
                        END
                    ), 2) AS avg_duration
                    FROM securecheck_ledger.police_stops
                    GROUP BY violation
                    ORDER BY avg_duration DESC;"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="violation",y="avg_duration",title="🕒 Average Stop Duration by Violation (minutes)")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🕒 Are night stops more likely to lead to arrests?":
                    sql = """SELECT
                    CASE
                        WHEN HOUR(stop_time) >= 20 OR HOUR(stop_time) < 6 THEN 'Night'
                        ELSE 'Day'
                    END AS time_period,
                    ROUND(AVG(is_arrested) * 100, 2) AS arrest_rate
                    FROM securecheck_ledger.police_stops
                    GROUP BY time_period;"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="time_period",y="arrest_rate",title="🕒 Arrest Rate Day vs Night (%)")
                    st.plotly_chart(fig, use_container_width=True)

        elif section == "⚖️ Violation-Based":
            query_option = st.selectbox("Choose an Analysis", [
                "⚖️ Violations most associated with searches or arrests",
                "⚖️ Violations most common among younger drivers (<25)",
                "⚖️ Violations that rarely result in search or arrest"
            ])
            run_query = st.button("▶️ Run Query")


            if run_query:

                if query_option == "⚖️ Violations most associated with searches or arrests":
                    sql = """SELECT violation,AVG(search_conducted)*100 as search_rate,AVG(is_arrested)*100 as arrest_rate
                    FROM police_stops 
                    GROUP BY violation 
                    ORDER BY search_rate DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="violation",y="search_rate",title="⚖️ Violations with Highest Search Rate (%)")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "⚖️ Violations most common among younger drivers (<25)":
                    sql = """SELECT violation, COUNT(*) as total 
                    FROM police_stops
                    WHERE driver_age < 25 
                    GROUP BY violation
                    ORDER BY total DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="violation",y="total",title="⚖️ Violations by Drivers Under 25")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "⚖️ Violations that rarely result in search or arrest":
                    sql = """SELECT violation, AVG(search_conducted)*100 as search_rate, AVG(is_arrested)*100 as arrest_rate
                    FROM police_stops 
                    GROUP BY violation 
                    ORDER BY search_rate ASC, arrest_rate ASC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="violation",y=["search_rate", "arrest_rate"],title="⚖️ Violations with Lowest Search/Arrest Rates (%)",
                    barmode="group")
                    st.plotly_chart(fig, use_container_width=True)

        elif section == "🌍 Location-Based":
            query_option = st.selectbox("Choose an Analysis", [
                "🌍 Countries reporting highest rate of drug-related stops",
                "🌍 Arrest rate by country and violation",
                "🌍 Which country has the most stops with search conducted"
            ])
            run_query = st.button("▶️ Run Query")


            if run_query:

                if query_option == "🌍 Countries reporting highest rate of drug-related stops":
                    sql = """SELECT country, AVG(drugs_related_stop)*100 as drug_rate 
                    FROM police_stops 
                    GROUP BY country
                    ORDER BY drug_rate DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="country",y="drug_rate",title="🌍 Drug-Related Stop Rate by Country (%)")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🌍 Arrest rate by country and violation":
                    sql = """SELECT country, violation, AVG(is_arrested)*100 as arrest_rate 
                    FROM police_stops 
                    GROUP BY country, violation
                    ORDER BY arrest_rate DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="arrest_rate",y="violation",color="country",orientation="h",title="🌍 Arrest Rate by Country & Violation (%)")
                    st.plotly_chart(fig, use_container_width=True)

                elif query_option == "🌍 Which country has the most stops with search conducted":
                    sql = """SELECT country, COUNT(*) as searches FROM police_stops WHERE search_conducted = TRUE GROUP BY country
                    ORDER BY searches DESC"""
                    results = fetch_data(sql)
                    st.dataframe(results)
                    fig = px.bar(results,x="country",y="searches",title="🌍 Searches by Country")
                    st.plotly_chart(fig, use_container_width=True)


    if analysis_section=="🔴 Complex":
        def load_lottieurl(url):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_animation = load_lottieurl("https://lottie.host/7a14797c-3147-4fee-be69-e72094ebf86c/nBFMhiTF5v.json")

        with st.sidebar:
            st_lottie(lottie_animation, speed=2, width=300, height=600, key="welcome_anim")
            
        st.subheader("🔴 Complex Analysis")
        query_option = st.selectbox("Choose an Analysis", [
            "📅 Yearly breakdown of stops and arrests by country",
            "📊 Driver violation trends by age and race",
            "⏱️ Time period analysis of stops (year/month/hour)",
            "📈 Violations with high search and arrest rates (ranked)",
            "🌐 Driver demographics by country (age/gender/race)",
            "🥇 Top 5 violations with highest arrest rates"
        ])
        run_query = st.button("▶️ Run Query")


        if run_query:
            if query_option == "📅 Yearly breakdown of stops and arrests by country":
                sql = """SELECT country,year,total_stops,total_arrests,
                    AVG(total_stops) OVER (PARTITION BY country ORDER BY year) AS cumulative_stops,
                    AVG(total_arrests) OVER (PARTITION BY country ORDER BY year) AS cumulative_arrests
                    FROM (
                        SELECT country,YEAR(stop_date) AS year,COUNT(*) AS total_stops,
                        SUM(is_arrested) AS total_arrests
                        FROM police_stops
                        GROUP BY country, YEAR(stop_date)
                    ) AS year_wise_data
                    ORDER BY country, year"""
                results = fetch_data(sql)
                st.dataframe(results)
                fig = px.bar(results,x="year",y="total_arrests",color="country",barmode="group",title="🔴 Yearly Arrests by Country",
                        labels={"total_arrests": "Total Arrests", "year": "Year"})
                st.plotly_chart(fig, use_container_width=True)
            
            elif query_option == "📊 Driver violation trends by age and race":
                sql = """
                    SELECT 
                    driver_race,
                    CASE
                        WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
                        WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
                        WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                        ELSE '60+'
                    END AS age_group,
                    violation,
                    COUNT(*) AS violation_count
                    FROM police_stops
                    GROUP BY driver_race, age_group, violation
                    ORDER BY driver_race, age_group"""

                results = fetch_data(sql)
                st.dataframe(results)
                fig = px.bar(results,x="violation",y="violation_count",color="age_group",
                        facet_col="driver_race",
                        title="📊 Driver Violation Trends by Age Group and Race",
                        labels={
                            "violation": "Violation",
                            "violation_count": "Count",
                            "age_group": "Age Group"
                        })
                st.plotly_chart(fig, use_container_width=True)

            elif query_option == "⏱️ Time period analysis of stops (year/month/hour)":
                sql = """
                    SELECT 
                    YEAR(stop_date) AS year,
                    MONTH(stop_date) AS month,
                    HOUR(stop_time) AS hour,
                    COUNT(*) AS total_stops
                    FROM police_stops
                    GROUP BY year, month, hour
                    ORDER BY year, month, hour"""
                results = fetch_data(sql)
                st.dataframe(results)
                fig = px.bar(results,x="hour",y="total_stops",color="month",
                        facet_col="year",
                        title="⏱️ Time Period Analysis of Stops (Year/Month/Hour)",
                        labels={
                            "total_stops": "Total Stops",
                            "hour": "Hour of Day"
                        })
                st.plotly_chart(fig, use_container_width=True)
            
            elif query_option == "📈 Violations with high search and arrest rates (ranked)":
                sql = """
                    SELECT 
                    violation,
                    COUNT(*) AS total_stops,
                    ROUND(100.0 * SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS search_rate_percent,
                    ROUND(100.0 * SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percent,
                    RANK() OVER (ORDER BY SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) DESC) AS search_rank,
                    RANK() OVER (ORDER BY SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) DESC) AS arrest_rank
                    FROM police_stops
                    GROUP BY violation
                    ORDER BY total_stops DESC"""

                results = fetch_data(sql)
                st.dataframe(results)
                fig = px.bar(
                        results,
                        x="violation",
                        y=["search_rate_percent", "arrest_rate_percent"],
                        title="📈 Violations with High Search and Arrest Rates (%)",
                        labels={"value": "Rate (%)", "variable": "Type"}
                    )
                st.plotly_chart(fig, use_container_width=True)


            elif query_option == "🌐 Driver demographics by country (age/gender/race)":
                sql="""
                    SELECT 
                    country,
                    driver_gender,
                    driver_race,
                    ROUND(AVG(driver_age), 1) AS avg_age,
                    COUNT(*) AS total_stops
                    FROM police_stops
                    GROUP BY country, driver_gender, driver_race
                    ORDER BY country, total_stops DESC"""
                results = fetch_data(sql)
                st.dataframe(results)
                fig = px.bar(results, x="country", y="total_stops", color="driver_gender",
                facet_col="driver_race", title="🌍 Driver Demographics by Country")
                st.plotly_chart(fig, use_container_width=True)

            elif query_option == "🥇 Top 5 violations with highest arrest rates":
                sql = """
                    SELECT 
                    violation,
                    AVG(is_arrested) * 100 AS arrest_rate
                    FROM police_stops
                    GROUP BY violation
                    ORDER BY arrest_rate DESC
                    LIMIT 5"""
                results = fetch_data(sql)
                st.dataframe(results)
                fig = px.bar(results, x="violation", y="arrest_rate",
                        title="🥇 Top 5 Violations with Highest Arrest Rates (%)",
                        labels={"arrest_rate": "Arrest Rate (%)"})
                st.plotly_chart(fig, use_container_width=True)
    
    if analysis_section=="📝 New Entry + Prediction":
        def load_lottieurl(url):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_animation = load_lottieurl("https://lottie.host/bcd26d44-2777-48b8-94e4-2a4c0b073290/EgXETD9kRu.json")

        with st.sidebar:
            st_lottie(lottie_animation, speed=1, width=300, height=600, key="welcome_anim")

        tab1, tab2 = st.tabs(["➕ New Entry", "📄 Recently Added / Delete"])
        with tab1:
            st.title("🚓 New Police Record Entry")
            st.header("Log New Stop & Predict Outcome")
            query = "SELECT * FROM police_stops"
            df = fetch_data(query)

            df["vehicle_number"] = df["vehicle_number"].astype(str)
            df["stop_date"] = pd.to_datetime(df["stop_date"]).dt.date
            df["stop_time"] = pd.to_datetime(df["stop_time"], format="%H:%M:%S").dt.time
            df["driver_age"] = df["driver_age"].astype(int)

            with st.form("traffic_entry_form"):
                st.subheader("📋 Entry Form")
            
                vehicle_number = st.text_input("Vehicle Number")
                country = st.selectbox("Country Name",["Canada","India","USA"])   
                stop_date = st.date_input("Stop Date", datetime.date.today())
                stop_time = st.time_input("Stop Time", value=datetime.datetime.now().time(), step=60)
                driver_gender = st.selectbox("Driver Gender", ["Male", "Female"])
                driver_age = st.number_input("Driver Age", min_value=18, max_value=100, value=19)
                driver_race = st.selectbox("Driver Race",["Asian","White","Black","Hispanic","Other"])
                violation = st.selectbox("Violation",["Speeding","Other","DUI","Seatbelt","Signal"])
                search_conducted = st.selectbox("Was a Search Conducted?", ["1","0"])
                search_type = st.selectbox("Search Type",["Vehicle Search","No Search","Frisk","Unknown"])
                drugs_related_stop = st.selectbox("drugs_related_stop", ["1","0"])
                stop_duration = st.selectbox("Stop Duration", ["16-30 Min","0-15 Min", "30+ Min"])

                submit_button = st.form_submit_button("Submit Entry")

                def get_most_common_outcome(violation, drugs_related_stop):
                    db = connect_to_database()
                    if db is None:
                        return "Warning"

                    try:
                        query = """
                            SELECT stop_outcome, COUNT(*) AS count
                            FROM police_stops
                            WHERE violation = %s AND drugs_related_stop = %s
                            GROUP BY stop_outcome
                            ORDER BY count DESC
                            LIMIT 1
                        """
                        cursor = db.cursor()
                        cursor.execute(query, (violation, drugs_related_stop))
                        result = cursor.fetchone()
                        return result[0] if result else "Warning"
                    finally:
                        db.close()


            if submit_button:
        
                stop_outcome = get_most_common_outcome(violation,drugs_related_stop)

                search_conducted_val = 1 if search_conducted else 0
                drugs_related_stop_val = 1 if drugs_related_stop else 0
                is_arrested_val = 1 if stop_outcome == "Arrest" else 0

                try:
                    query = """
                        INSERT INTO police_stops (
                            country, vehicle_number, stop_date, stop_time,
                            driver_gender, driver_age, driver_race, violation,
                            search_conducted, search_type, stop_outcome,
                            is_arrested, drugs_related_stop, stop_duration
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    
                    formatted_time = stop_time.strftime("%H:%M:%S")

                    display_time = stop_time.strftime("%I.%M %p").lstrip("0").upper()

                
                    db = connect_to_database()
                    cursor = db.cursor()
                    cursor.execute(query, (
                        country, vehicle_number, stop_date, formatted_time,
                        driver_gender, driver_age, driver_race, violation,
                        search_conducted_val, search_type, stop_outcome,
                        is_arrested_val, drugs_related_stop_val, stop_duration
                    ))
                    db.commit()
                    db.close()
                    st.success("✅ New entry inserted successfully into the database.")

                    fetch_query = """
                        SELECT * FROM police_stops
                        WHERE vehicle_number = %s AND stop_date = %s AND stop_time = %s
                    """
                    db = connect_to_database()
                    new_entry = pd.read_sql(fetch_query, db, params=(vehicle_number, stop_date, formatted_time))
                    db.close()

                    st.subheader("📊 Review New Police Entry")
                    st.dataframe(new_entry)

                    outcome_text = {
                        "Ticket": "and the driver received a ticket",
                        "Arrest": "and the driver was arrested",
                        "Warning": "and the driver was warned"
                    }.get(stop_outcome, f"and the outcome was {stop_outcome}")

                    search_text = "A search was conducted." if search_conducted else "No search was conducted."
                    drugs_text = "It was drug-related." if drugs_related_stop else "It was not drug-related."

                    st.success(f"**Violation:** {violation}")
                    st.success(f"**Stop Outcome:** {stop_outcome}")
                    
                    summary = (
                            f"🚗 On **{stop_date}**, a **{driver_age}**-year-old **{driver_gender}** driver was stopped for **{violation}** "
                            f"at **{display_time}**. **{search_text}**, **{outcome_text}**. "
                            f"The stop lasted **{stop_duration}** **{drugs_text}**"
                        )
                    st.subheader("🎯 Prediction Summary")
                    st.markdown(summary)

                except Exception as e:
                    st.error(f"❌ Error inserting into DB: {e}")
                
        with tab2:

            st.header("Recently Added Records")
            db = connect_to_database()
            if db:
                query = "SELECT * FROM police_stops ORDER BY stop_date DESC,stop_time DESC LIMIT 10"
                df_recent = pd.read_sql(query, db)

                if not df_recent.empty:
                    st.dataframe(df_recent)

                    vehicle_to_delete = st.selectbox( "Select Vehicle Number to Delete:",
                        df_recent["vehicle_number"].unique())
                    stoptime_to_delete = st.selectbox("Select the Stop Time to Delete :",df_recent['stop_time'].unique())

                    if st.button("❌ Delete Selected Entry"):
                        try:
                            cursor = db.cursor()
                            delete_query = "DELETE FROM police_stops WHERE vehicle_number = %s and stop_time = %s"
                            cursor.execute(delete_query, (vehicle_to_delete,stoptime_to_delete))
                            db.commit()
                            st.success(f"✅ Entry with Vehicle Number **{vehicle_to_delete}** on **{stoptime_to_delete}** deleted successfully.")
                            df_recent = pd.read_sql(query, db)
                            st.subheader("📋 Updated Records After Deletion")
                            st.dataframe(df_recent)
                        except Exception as e:
                            st.error(f"❌ Error deleting from DB: {e}")
                        finally:
                            db.close()

                else:
                    st.info("No recent records found.")

        
    

