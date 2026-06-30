import yfinance as yf

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "symbol": ticker,
            "name": info.get("longName", "N/A"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "change": info.get("regularMarketChange", 0),
            "changePct": info.get("regularMarketChangePercent", 0),
            "volume": info.get("volume", 0),
            "marketCap": info.get("marketCap", 0),
            "pe": info.get("trailingPE", 0),
            "high52w": info.get("fiftyTwoWeekHigh", 0),
            "low52w": info.get("fiftyTwoWeekLow", 0),
        }
    except Exception as e:
        return {"error": str(e)}

def get_history(ticker, period="3mo"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)
        return df[["Date","Open","High","Low","Close","Volume"]].to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

def get_indicators(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)
        return df[["Date","Close","MA20","MA50","RSI"]].dropna().to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}