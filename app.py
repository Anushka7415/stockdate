import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Live Stock Market Dashboard")

# Sidebar
st.sidebar.header("Settings")

search_text = st.sidebar.text_input(
    "Search Stock",
    placeholder="Type company name or symbol..."
)

ticker = None

if search_text:
    search_results = yf.Search(
        search_text,
        max_results=10,
        news_count=0
    ).quotes

    suggestions = {}

    for item in search_results:
        symbol = item.get("symbol")
        name = (
            item.get("longname")
            or item.get("shortname")
            or symbol
        )

        if symbol:
            suggestions[f"{name} ({symbol})"] = symbol

    if suggestions:
        selected_stock = st.sidebar.selectbox(
            "Matching stocks",
            options=list(suggestions.keys())
        )

        ticker = suggestions[selected_stock]
    else:
        st.sidebar.warning("No matching stock found")
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"])
auto_refresh = st.sidebar.checkbox("Auto Refresh (60s)")

if ticker and st.sidebar.button("Analyze"):
    try:
        # Data fetch
        stock = yf.Ticker(ticker)
        info = stock.info
        df = stock.history(period=period)

        # Company name
        st.subheader(f"{info.get('longName', ticker)} ({ticker.upper()})")

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        currency = info.get('currency', 'USD')
        symbol = '₹' if currency == 'INR' else '$'
        change = info.get('regularMarketChange', 0)
        changePct = info.get('regularMarketChangePercent', 0)
        volume = info.get('volume', 0)
        marketCap = info.get('marketCap', 0)
        col1.metric("💰 Price", f"{symbol}{price:.2f}", f"{changePct:.2f}%")
        col2.metric("📊 Volume", f"{volume:,}")
        col3.metric("🏢 Market Cap", f"{symbol}{marketCap/1e9:.1f}B")
        col4.metric("📅 52W High", f"{symbol}{info.get('fiftyTwoWeekHigh', 0):.2f}")
       
        
       
      
        # Moving averages
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # Main Chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.7, 0.3],
            subplot_titles=("Price + Moving Averages", "RSI")
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"],
            high=df["High"], low=df["Low"], close=df["Close"],
            name="Price"
        ), row=1, col=1)

        # MA lines
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MA20"],
            name="MA20", line=dict(color="orange", width=1.5)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df["MA50"],
            name="MA50", line=dict(color="blue", width=1.5)
        ), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI"],
            name="RSI", line=dict(color="purple", width=1.5)
        ), row=2, col=1)

        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        fig.update_layout(
            height=700,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Auto refresh
        if auto_refresh:
            import time
            time.sleep(60)
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e} — Check ticker symbol!")
