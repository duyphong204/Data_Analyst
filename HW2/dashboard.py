# findash_app_fixed.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from yahoo_fin import stock_info as si
import requests

st.set_page_config(page_title="FinDash (fixed)", layout="wide")


# -------------------------
# Helpers
# -------------------------
@st.cache_data(show_spinner=False)
def get_sp500_tickers():
    """
    Lấy danh sách S&P500 từ Wikipedia với header (User-Agent).
    Nếu lỗi, trả về 1 list mặc định nhỏ để tránh crash.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        tables = pd.read_html(resp.text)
        if len(tables) > 0:
            df = tables[0]
            # Một số phiên bản wiki có cột 'Symbol' hoặc 'Ticker'
            if 'Symbol' in df.columns:
                return df['Symbol'].astype(str).str.replace('.', '-', regex=False).tolist()
            elif 'Ticker' in df.columns:
                return df['Ticker'].astype(str).str.replace('.', '-', regex=False).tolist()
        # fallback
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    except Exception:
        # fallback nhỏ
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']


def safe_yf_download(ticker, **kwargs):
    """Bao wrapper cho yf.download để trả dataframe an toàn."""
    try:
        df = yf.download(ticker, **kwargs)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def safe_si_get(func, *args, **kwargs):
    """Gọi các hàm yahoo_fin.stock_info an toàn, trả None khi lỗi."""
    try:
        return func(*args, **kwargs)
    except Exception:
        return None


# -------------------------
# Tab 1: Summary
# -------------------------
def tab1(ticker):
    import streamlit as st
    import pandas as pd
    import numpy as np
    import yfinance as yf
    import plotly.express as px
    from datetime import datetime

    st.title("Summary")

    if ticker == '-' or not ticker:
        st.info("Select ticker on the left to begin.")
        return

    st.write(ticker)

    # ========== HÀM HỖ TRỢ ==========
    @st.cache_data(show_spinner=False)
    def safe_yf_download(ticker, period="1y"):
        try:
            data = yf.download(ticker, period=period, progress=False)
            if not data.empty:
                return data
        except Exception:
            pass
        return pd.DataFrame()

    def safe_float(x):
        if isinstance(x, (list, np.ndarray, pd.Series)):
            try:
                return float(x[0])
            except Exception:
                return np.nan
        try:
            return float(x)
        except Exception:
            return np.nan

    # ========== LẤY DỮ LIỆU ==========
    data = safe_yf_download(ticker, period="2y")
    if data.empty:
        st.warning("Không có dữ liệu giá để hiển thị.")
        return

    info = yf.Ticker(ticker).info

    last_close = safe_float(data["Close"].iloc[-1])
    open_price = safe_float(data["Open"].iloc[-1])
    high_today = safe_float(data["High"].iloc[-1])
    low_today = safe_float(data["Low"].iloc[-1])
    high_52 = safe_float(data["High"].tail(252).max())
    low_52 = safe_float(data["Low"].tail(252).min())
    volume = int(safe_float(data["Volume"].iloc[-1]))
    avg_volume = int(safe_float(data["Volume"].mean()))

    # ========== CHUYỂN ĐỔI DỮ LIỆU ==========
    def fmt_cap(x):
        if not x or np.isnan(x): return "-"
        if x >= 1e12: return f"{x/1e12:.3f}T"
        elif x >= 1e9: return f"{x/1e9:.3f}B"
        elif x >= 1e6: return f"{x/1e6:.3f}M"
        else: return f"{x:,.0f}"

    market_cap = info.get("marketCap")
    beta = info.get("beta")
    pe = info.get("trailingPE")
    eps = info.get("trailingEps")
    div_yield = info.get("dividendYield")
    dividend = info.get("dividendRate")
    target = info.get("targetMeanPrice")
    ex_div = info.get("exDividendDate")
    earnings_date = info.get("earningsDate")

    # ========== TẠO 2 BẢNG THÔNG TIN ==========
    left = pd.DataFrame({
        "attribute": [
            "Previous Close", "Open", "Bid", "Ask",
            "Day's Range", "52 Week Range", "Volume", "Avg. Volume"
        ],
        "value": [
            f"{last_close:.2f}" if not np.isnan(last_close) else "-",
            f"{open_price:.2f}" if not np.isnan(open_price) else "-",
            "-",
            "-",
            f"{low_today:.2f} - {high_today:.2f}" if not np.isnan(high_today) else "-",
            f"{low_52:.2f} - {high_52:.2f}" if not np.isnan(high_52) else "-",
            f"{volume:,}" if volume else "-",
            f"{avg_volume:,}" if avg_volume else "-"
        ]
    })

    right = pd.DataFrame({
        "attribute": [
            "Market Cap", "Beta (5Y Monthly)", "PE Ratio (TTM)",
            "EPS (TTM)", "Earnings Date",
            "Forward Dividend & Yield", "Ex-Dividend Date", "1y Target Est"
        ],
        "value": [
            fmt_cap(market_cap),
            f"{beta:.2f}" if beta else "-",
            f"{pe:.2f}" if pe else "-",
            f"{eps:.2f}" if eps else "-",
            str(earnings_date[0].date()) if isinstance(earnings_date, list) and len(earnings_date) > 0 else "-",
            f"{dividend or 0:.2f} ({div_yield*100:.2f}%)" if div_yield else "-",
            str(datetime.fromtimestamp(ex_div).date()) if isinstance(ex_div, (int, float)) else "-",
            f"{target:.2f}" if target else "-"
        ]
    })

    # ========== HIỂN THỊ 2 CỘT ==========
    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(left.set_index("attribute"))
    with c2:
        st.dataframe(right.set_index("attribute"))

    # ========== HIỂN THỊ BIỂU ĐỒ ==========
        # --- HIỂN THỊ BIỂU ĐỒ GIÁ ĐÓNG CỬA ---
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]

    df_chart = pd.DataFrame({
        "Date": data.index,
        "Close": data["Close"].apply(
            lambda x: float(x[0]) if isinstance(x, (list, np.ndarray, pd.Series)) else float(x)
        )
    })

    fig = px.area(
        df_chart,
        x="Date",
        y="Close",
        title=f"{ticker} - Closing Price (2Y History)"
    )

    fig.update_traces(line_color="#1976d2", fillcolor="rgba(25,118,210,0.4)")

    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(label="MAX", step="all")
            ])
        ),
        rangeslider_visible=True
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=80, b=60),
        xaxis=dict(
            title=dict(
                text="Date",
                standoff=15
            )
        ),
        yaxis=dict(
            title=dict(
                text="Close",
                standoff=10
            )
        ),
        font=dict(size=13),
    )

    st.plotly_chart(fig, use_container_width=True)



# -------------------------
# Tab 2: Chart
# -------------------------
def tab2(ticker):
    st.title("Chart")
    if ticker == '-' or not ticker:
        st.info("Chọn ticker ở sidebar để bắt đầu.")
        return

    st.write(f"Ticker: {ticker}")
    st.write("Set duration to '-' để chọn khoảng ngày cụ thể")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        start_date = st.date_input("Start date", datetime.today().date() - timedelta(days=30))
    with c2:
        end_date = st.date_input("End date", datetime.today().date())
    with c3:
        duration = st.selectbox("Select duration", ['-', '1Mo', '3Mo', '6Mo', 'YTD', '1Y', '3Y', '5Y', 'MAX'])
    with c4:
        inter = st.selectbox("Select interval", ['1d', '1wk', '1mo'])
    with c5:
        plot = st.selectbox("Select Plot", ['Line', 'Candle'])

    @st.cache_data(show_spinner=False)
    def get_chart_data(t, duration, start_date, end_date, inter):
        # SMA từ toàn bộ lịch sử
        sma_all = safe_yf_download(t, period='max')
        if not sma_all.empty and 'Close' in sma_all.columns:
            sma_all['SMA'] = sma_all['Close'].rolling(50).mean()
            sma_df = sma_all.reset_index()[['Date', 'SMA']]
        else:
            sma_df = pd.DataFrame(columns=['Date', 'SMA'])

        if duration != '-':
            df = safe_yf_download(t, period=duration, interval=inter).reset_index()
        else:
            df = safe_yf_download(t, start=start_date, end=end_date + timedelta(days=1), interval=inter).reset_index()
        if df.empty:
            return df
        # đảm bảo cột Date tồn tại
        if 'Date' not in df.columns and df.index.name in [None, 'Date']:
            df = df.reset_index().rename(columns={df.columns[0]: 'Date'}) if 'Date' not in df.columns else df
        # merge SMA nếu có
        if not sma_df.empty and 'Date' in df.columns:
            df = df.merge(sma_df, on='Date', how='left')
        else:
            df['SMA'] = np.nan
        return df

    chartdata = get_chart_data(ticker, duration, start_date, end_date, inter)
    if chartdata.empty:
        st.warning("Không có dữ liệu để vẽ.")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if plot == 'Line':
        fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['Close'], mode='lines', name='Close'), secondary_y=False)
    else:
        # Candlestick - nếu thiếu cột sẽ báo, nên kiểm tra
        if all(col in chartdata.columns for col in ['Open', 'High', 'Low', 'Close']):
            fig.add_trace(go.Candlestick(x=chartdata['Date'], open=chartdata['Open'], high=chartdata['High'],
                                         low=chartdata['Low'], close=chartdata['Close'], name='Candle'))
        else:
            st.warning("Dữ liệu chưa đủ cho biểu đồ Candle. Hiển thị Line thay thế.")
            fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['Close'], mode='lines', name='Close'), secondary_y=False)

    fig.add_trace(go.Scatter(x=chartdata['Date'], y=chartdata['SMA'], mode='lines', name='50-day SMA'), secondary_y=False)
    if 'Volume' in chartdata.columns:
        fig.add_trace(go.Bar(x=chartdata['Date'], y=chartdata['Volume'], name='Volume'), secondary_y=True)
        try:
            fig.update_yaxes(range=[0, chartdata['Volume'].max() * 3], showticklabels=False, secondary_y=True)
        except Exception:
            pass

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# Tab 3: Statistics (đã cố gắng giữ nguyên nhưng an toàn hơn)
# -------------------------
def tab3(ticker):
    st.title("Statistics")
    if ticker == '-' or not ticker:
        st.info("Chọn ticker.")
        return
    st.write(f"Ticker: {ticker}")

    @st.cache_data(show_spinner=False)
    def get_stats_safe(t):
        return safe_si_get(si.get_stats, t)

    @st.cache_data(show_spinner=False)
    def get_stats_valuation_safe(t):
        return safe_si_get(si.get_stats_valuation, t)

    val = get_stats_valuation_safe(ticker)
    stats = get_stats_safe(ticker)

    c1, c2 = st.columns(2)
    with c1:
        st.header("Valuation Measures")
        if val is None or val.empty:
            st.write("No valuation data.")
        else:
            try:
                df_val = val.copy()
                df_val[1] = df_val[1].astype(str)
                df_val = df_val.rename(columns={0: 'Attribute', 1: ''}).set_index('Attribute')
                st.table(df_val)
            except Exception:
                st.dataframe(val)

        st.header("Financial Highlights")
        if stats is None or stats.empty:
            st.write("No stats data.")
        else:
            try:
                stats2 = stats.copy()
                if 'Attribute' not in stats2.columns:
                    stats2 = stats2.reset_index().rename(columns={0: 'Attribute', 1: 'Value'})
                stats2['Value'] = stats2['Value'].astype(str)
                stats2 = stats2.set_index('Attribute')
                # chọn các khu vực an toàn (nếu có)
                display_slices = [
                    (29, 31), (31, 33), (33, 35), (35, 43), (43, 49), (49, None)
                ]
                for s,e in display_slices:
                    st.subheader(f"Rows {s} to {e or 'end'}")
                    try:
                        st.table(stats2.iloc[s:e,])
                    except Exception:
                        st.write("Không thể hiển thị đoạn này.")
            except Exception:
                st.dataframe(stats)
    with c2:
        st.header("Trading Information")
        if stats is None or stats.empty:
            st.write("No stats.")
        else:
            try:
                stats2 = stats.copy()
                if 'Attribute' not in stats2.columns:
                    stats2 = stats2.reset_index().rename(columns={0: 'Attribute', 1: 'Value'})
                stats2 = stats2.set_index('Attribute')
                st.subheader("Stock Price History")
                try:
                    st.table(stats2.iloc[:7,])
                except Exception:
                    st.write("Không có dữ liệu.")
                st.subheader("Share Statistics")
                try:
                    st.table(stats2.iloc[7:19,])
                except Exception:
                    st.write("Không có dữ liệu.")
                st.subheader("Dividends & Splits")
                try:
                    st.table(stats2.iloc[19:29,])
                except Exception:
                    st.write("Không có dữ liệu.")
            except Exception:
                st.write("Không thể xử lý stats.")


# -------------------------
# Tab 4: Financials
# -------------------------
def tab4(ticker):
    st.title("Financials")
    if ticker == '-' or not ticker:
        st.info("Chọn ticker.")
        return
    st.write(f"Ticker: {ticker}")

    statement = st.selectbox("Show", ['Income Statement', 'Balance Sheet', 'Cash Flow'])
    period = st.selectbox("Period", ['Yearly', 'Quarterly'])

    @st.cache_data(show_spinner=False)
    def get_income_yearly(t):
        return safe_si_get(si.get_income_statement, t)

    @st.cache_data(show_spinner=False)
    def get_income_quarterly(t):
        return safe_si_get(si.get_income_statement, t, yearly=False)

    @st.cache_data(show_spinner=False)
    def get_balance_yearly(t):
        return safe_si_get(si.get_balance_sheet, t)

    @st.cache_data(show_spinner=False)
    def get_balance_quarterly(t):
        return safe_si_get(si.get_balance_sheet, t, yearly=False)

    @st.cache_data(show_spinner=False)
    def get_cash_yearly(t):
        return safe_si_get(si.get_cash_flow, t)

    @st.cache_data(show_spinner=False)
    def get_cash_quarterly(t):
        return safe_si_get(si.get_cash_flow, t, yearly=False)

    data = None
    if statement == 'Income Statement' and period == 'Yearly':
        data = get_income_yearly(ticker)
    elif statement == 'Income Statement' and period == 'Quarterly':
        data = get_income_quarterly(ticker)
    elif statement == 'Balance Sheet' and period == 'Yearly':
        data = get_balance_yearly(ticker)
    elif statement == 'Balance Sheet' and period == 'Quarterly':
        data = get_balance_quarterly(ticker)
    elif statement == 'Cash Flow' and period == 'Yearly':
        data = get_cash_yearly(ticker)
    elif statement == 'Cash Flow' and period == 'Quarterly':
        data = get_cash_quarterly(ticker)

    if data is None:
        st.warning("Không lấy được báo cáo tài chính.")
    else:
        try:
            st.dataframe(data)
        except Exception:
            st.write(data)


# -------------------------
# Tab 5: Analysis (Analysts info)
# -------------------------
def tab5(ticker):
    st.title("Analysis")
    st.write("Currency in USD")
    if ticker == '-' or not ticker:
        st.info("Chọn ticker.")
        return

    @st.cache_data(show_spinner=False)
    def get_analysis(t):
        try:
            return si.get_analysts_info(t)
        except Exception:
            return None

    analysis = get_analysis(ticker)
    if not analysis:
        st.warning("Không lấy được analysts info.")
        return

    # analysis là dict, mỗi mục là dataframe
    for k, v in analysis.items():
        st.subheader(str(k))
        try:
            st.dataframe(v)
        except Exception:
            st.write(v)


# -------------------------
# Tab 6: Monte Carlo
# -------------------------
def tab6(ticker):
    st.title("Monte Carlo Simulation")
    if ticker == '-' or not ticker:
        st.info("Chọn ticker.")
        return

    simulations = st.selectbox("Number of Simulations (n)", [200, 500, 1000])
    time_horizon = st.selectbox("Time Horizon (t)", [30, 60, 90])

    @st.cache_data(show_spinner=False)
    def montecarlo_sim(t, time_horizon, simulations):
        # dùng dữ liệu 60 ngày làm estimation để ổn định hơn
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=60)

        df = safe_yf_download(t, start=start_date, end=end_date + timedelta(days=1))
        if df.empty or 'Close' not in df.columns:
            return pd.DataFrame()

        close_price = df['Close']
        daily_return = close_price.pct_change().dropna()
        if daily_return.empty:
            return pd.DataFrame()

        daily_volatility = daily_return.std()

        simulation_df = pd.DataFrame()
        last_price = close_price.iloc[-1]

        for i in range(simulations):
            prices = []
            price = last_price
            for _ in range(time_horizon):
                shock = np.random.normal(0, daily_volatility)
                price = price * (1 + shock)
                prices.append(price)
            simulation_df[i] = prices
        return simulation_df

    mc = montecarlo_sim(ticker, time_horizon, simulations)
    if mc.empty:
        st.warning("Không thể thực hiện mô phỏng do thiếu dữ liệu.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(mc)
    ax.set_title(f'Monte Carlo simulation for {ticker} for {time_horizon} days')
    ax.set_xlabel('Day')
    ax.set_ylabel('Price')
    last_price = safe_yf_download(ticker, period='5d')['Close'].iloc[-1] if not safe_yf_download(ticker, period='5d').empty else None
    if last_price is not None:
        ax.axhline(y=last_price, color='red', linestyle='--', label=f'Current price: {last_price:.2f}')
        ax.legend()
    st.pyplot(fig)

    ending_prices = mc.iloc[-1, :].values
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.hist(ending_prices, bins=50)
    p5 = np.percentile(ending_prices, 5)
    ax2.axvline(p5, color='red', linestyle='--', linewidth=1)
    ax2.set_title('Distribution of the Ending Price')
    st.pyplot(fig2)

    if last_price is not None:
        VaR = last_price - p5
        st.write(f'VaR at 95% confidence interval is: {VaR:.2f} USD')


# -------------------------
# Tab 7: Portfolio Trend
# -------------------------
def tab7():
    st.title("Your Portfolio's Trend")
    tickers = get_sp500_tickers()
    selected = st.multiselect("Select tickers", options=tickers, default=['AAPL'] if 'AAPL' in tickers else tickers[:1])
    if not selected:
        st.info("Chọn ít nhất 1 ticker.")
        return

    df = pd.DataFrame()
    for t in selected:
        tmp = safe_yf_download(t, period='5y')
        if tmp.empty:
            st.warning(f"No data for {t}")
            continue
        df[t] = tmp['Close']
    if df.empty:
        st.warning("Không có dữ liệu cho các ticker đã chọn.")
        return
    fig = px.line(df, title="Portfolio trend (Close prices)")
    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# Main run
# -------------------------
def run():
    st.sidebar.title("FinDash (fixed)")
    ticker_list = ['-'] + get_sp500_tickers()
    ticker = st.sidebar.selectbox("Select a ticker", ticker_list)
    tab = st.sidebar.radio("Select tab", ['Summary', 'Chart', 'Statistics', 'Financials', 'Analysis', 'Monte Carlo Simulation', "Your Portfolio's Trend"])

    if tab == 'Summary':
        tab1(ticker)
    elif tab == 'Chart':
        tab2(ticker)
    elif tab == 'Statistics':
        tab3(ticker)
    elif tab == 'Financials':
        tab4(ticker)
    elif tab == 'Analysis':
        tab5(ticker)
    elif tab == 'Monte Carlo Simulation':
        tab6(ticker)
    elif tab == "Your Portfolio's Trend":
        tab7()


if __name__ == "__main__":
    run()
