import yahoo_fin.stock_info as si
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
#import pyfolio as pf
#==============================================================================
# Main body
#==============================================================================

#==============================================================================
# Tab 1 Summary
#==============================================================================
def tab1():
    st.title("Summary")
    st.write("Select ticker on the left to begin")
    st.write(ticker)

    # --- HÀM LẤY DỮ LIỆU TỪ YFINANCE (THAY CHO yahoo_fin) ---
    def getsummary(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info
        data = {
            "Previous Close": info.get("previousClose"),
            "Open": info.get("open"),
            "Bid": info.get("bid"),
            "Ask": info.get("ask"),
            "Day's Range": f"{info.get('dayLow')} - {info.get('dayHigh')}",
            "52 Week Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
            "Volume": info.get("volume"),
            "Avg. Volume": info.get("averageVolume"),
            "Market Cap": info.get("marketCap"),
            "Beta (5Y Monthly)": info.get("beta"),
            "PE Ratio (TTM)": info.get("trailingPE"),
            "EPS (TTM)": info.get("trailingEps"),
            "Earnings Date": info.get("earningsDate"),
            "Forward Dividend & Yield": info.get("dividendYield"),
            "Ex-Dividend Date": info.get("exDividendDate"),
            "1y Target Est": info.get("targetMeanPrice")
        }
        df = pd.DataFrame(data.items(), columns=["attribute", "value"])
        return df

    # --- HIỂN THỊ 2 CỘT (giống bản gốc) ---
    c1, c2 = st.columns((1, 1))

    if ticker != '-':
        summary = getsummary(ticker)
        summary['value'] = summary['value'].astype(str)

        # Nếu có ít dòng hơn 16 thì dùng min() để tránh lỗi
        n = len(summary)
        left_idx = [i for i in [14, 12, 5, 2, 6, 1, 16, 3] if i < n]
        right_idx = [i for i in [11, 4, 13, 7, 8, 10, 9, 0] if i < n]

        with c1:
            showsummary = summary.iloc[left_idx]
            showsummary.set_index('attribute', inplace=True)
            st.dataframe(showsummary)

        with c2:
            showsummary = summary.iloc[right_idx]
            showsummary.set_index('attribute', inplace=True)
            st.dataframe(showsummary)

    # --- VẼ BIỂU ĐỒ GIÁ ---
    @st.cache_data
    def getstockdata(ticker):
        try:
            ticker = ticker.replace('.', '-')
            data = yf.download(ticker, period='MAX')
            return data
        except Exception as e:
            st.error(f"Lỗi khi tải dữ liệu từ Yahoo Finance: {e}")
            return pd.DataFrame()

    if ticker != '-':
        chartdata = getstockdata(ticker)

        if chartdata.empty or 'Close' not in chartdata.columns:
            st.warning(f"⚠️ Không có dữ liệu giá cho mã {ticker}.")
        else:
            # Chỉ lấy cột Close, đảm bảo nó là Series 1D
            chartdata['Close'] = chartdata['Close'].astype(float)
            fig = px.area(chartdata, x=chartdata.index, y='Close', title=f'{ticker} Price History')

            fig.update_xaxes(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=3, label="3Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(label="MAX", step="all")
                    ])
                )
            )
            st.plotly_chart(fig, use_container_width=True)


             
        
def safe_tickers_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Báo lỗi nếu request thất bại
    tables = pd.read_html(response.text)
    return tables[0]['Symbol'].tolist()
            
def run():
    
    # Add the ticker selection on the sidebar
    # Get the list of stock tickers from S&P500
    ticker_list = ['-'] + safe_tickers_sp500()
    
    # Add selection box
    global ticker
    ticker = st.sidebar.selectbox("Select a ticker", ticker_list)
    
    
    # Add a radio box
    select_tab = st.sidebar.radio("Select tab", ['Summary', 'Chart', 'Statistics', 'Financials', 'Analysis', 'Monte Carlo Simulation', "Your Portfolio's Trend"])
    
    # Show the selected tab
    if select_tab == 'Summary':
        tab1()
    # elif select_tab == 'Chart':
    #     tab2()
    # elif select_tab == 'Statistics':
    #     tab3()
    # elif select_tab == 'Financials':
    #     tab4()
    # elif select_tab == 'Analysis':
    #     tab5()
    # elif select_tab == 'Monte Carlo Simulation':
    #     tab6()
    # elif select_tab == "Your Portfolio's Trend":
    #     tab7()
       
    
if __name__ == "__main__":
    run() 