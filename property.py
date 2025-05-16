import streamlit as st
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import pandas as pd
import time
import plotly.express as px

# Streamlit App Title
st.set_page_config(page_title="📊 Property Search Trend Analyzer", layout="wide")
st.title("📊 Property Search Trend Analyzer")

# Keyword input from user
keywords_input = st.text_input("Enter keywords (comma separated)", 
                               "2BHK,3BHK,1BHK,farmhouse")
keyword_list = [k.strip() for k in keywords_input.split(",") if k.strip()]

# Sidebar for custom date range selection
st.sidebar.subheader("📅 Select Date Range")
start_date = st.sidebar.date_input("Start date", pd.to_datetime("2025-04-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("2025-04-30"))

# Check date validity
if start_date > end_date:
    st.error("Start date must be before end date")
else:
    timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"

    # Define function to safely get trends data
    def get_trends_data(keywords, timeframe, max_retries=5, sleep_time=60):
        pytrends = TrendReq(hl='en-IN', tz=330)
        attempt = 0
        while attempt < max_retries:
            try:
                pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='IN', gprop='')
                time.sleep(3)  # Respect API limits
                data = pytrends.interest_over_time()
                return data
            except TooManyRequestsError:
                st.warning("Too many requests. Waiting before retrying...")
                time.sleep(sleep_time)
                attempt += 1
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                break
        return None

    # Fetch the data
    if keyword_list:
        with st.spinner("Fetching trend data..."):
            data = get_trends_data(keyword_list, timeframe)

        if data is not None and not data.empty:
            st.subheader("📈 Search Trends Over Time")
            df = data.reset_index()
            fig = px.line(df, x='date', y=keyword_list, title='Google Search Trends')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for the selected keywords and time range.")
