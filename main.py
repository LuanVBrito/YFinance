import yfinance as yf
import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import plotly.express as px
import plotly.graph_objects as go


#.venv\Scripts\activate


load_dotenv()
API_KEY = os.getenv("SERP_API_KEY")

st.set_page_config(layout="wide")
st.header("Finance Dashboard")


@st.cache_data
def get_company_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = pd.read_html(requests.get(url, headers=headers).text)[0]
    return data["Symbol"].unique()


def get_selected_ticker(ticker):
    return yf.Ticker(select_company)
#st.cache_data
def get_selected_ticker(ticker_symbol):
    return yf.Ticker(ticker_symbol)

@st.cache_data
def get_company_imagem(searchword, key):
    params = {"engine": "google",
          "q": searchword,
          "tbm": "isch",
          "api_key":key}

    search = GoogleSearch(params)
    results = search.get_dict()
    result = results['images_results'][0]
    return result["original"]


company_list = get_company_tickers()
select_company = st.selectbox(label="Select a company",options=company_list)
selected_ticker = get_selected_ticker(select_company)
company_data = get_selected_ticker(select_company).info
action_history = selected_ticker.history(period="max").reset_index()
min_date = action_history["Date"].min()
max_date = action_history["Date"].max()


with st.sidebar:
    st.image(get_company_imagem(company_data.get('shortName', 'N/a'), API_KEY))
    st.markdown(f"""
    ### Company Informations
                
    **Name:** {company_data.get("shortName", "N/A")}    
    **Sector:** {company_data.get("sector", "N/A")}     
    Industry: {company_data.get("industry", "N/A")}     
    Symbol: {company_data.get("symbol", "N/A")}     
    Country: {company_data.get("country", "N/A")}   
    Currency: {company_data.get("currency", "N/A")}     
    Website: {company_data.get("website", "N/A")}   

    ## Finance data
    **Market Cap**: {company_data.get("marketCap", "N/A"):,}    
    **Current Price**: {company_data.get("currentPrice", "N/A")}    
    **Target Mean Price**: {company_data.get("targetMeanPrice", "N/A")}  
    **Dividend Yield**: {company_data.get("dividendYield", "N/A")}  
    **P/L (PE Ratio)**: {company_data.get("traillingPE", "N/A")}    
    """)
    min_select, max_select = st.select_slider(label="Select time interval",options=action_history["Date"], value=(min_date, max_date))

df_filtered = action_history[(action_history["Date"] <= max_select) &  (action_history["Date"] >= min_select )]
df_filtered["avarage moving"] = df_filtered["Close"].rolling(window=50).mean()


line_chart_low = px.line(data_frame=df_filtered, x="Date", y="Low", title="'Low' value of shares over time")
line_chart_high = px.line(data_frame=df_filtered, x="Date", y="High",title="'High' value of shares over time")
low_high_comparision = px.line(data_frame=df_filtered, x="Date", y=["Open", "Close"],
                               color_discrete_map={"Open": "blue", "Close": "grey"}, title="Comparison of opening and closing stock prices")
avarage_moving_comparision = px.line(data_frame=df_filtered, x="Date", y=["avarage moving", "Close"],
                                     color_discrete_map={"avarage moving": "blue", "Close": "grey"}, title="Comparison between closing value and moving average of shares")

historiogram_closes = px.histogram(data_frame=df_filtered, x="Close", nbins=50, title="Distribution of closing values")

column1, column2 = st.columns(2)

with column1:
    st.plotly_chart(line_chart_low)
with column2:
    st.plotly_chart(line_chart_high)

st.plotly_chart(low_high_comparision)

sub_column1, sub_columns2 = st.columns([3,1])

with sub_column1:
    st.plotly_chart(historiogram_closes)
with sub_columns2:
    st.plotly_chart(avarage_moving_comparision)

fig_candlestick = go.Figure(data=[go.Candlestick(x=df_filtered["Date"],
                                                 open=df_filtered["Open"],
                                                 high=df_filtered["High"],
                                                 low=df_filtered["Low"],
                                                 close=df_filtered["Close"])])
fig_candlestick.update_layout(title="Candlestick Chart (Opening and Closing Prices, High and Low)",
                              xaxis_rangeslider_visible=False)
st.plotly_chart(fig_candlestick)

with st.expander(label="Data Download"):
    st.dataframe(df_filtered)
    st.download_button(label="download", data=df_filtered.to_csv(), file_name="data.csv")