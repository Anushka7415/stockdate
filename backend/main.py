from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stock_data import get_stock_info, get_history, get_indicators

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stock/{ticker}")
def stock_info(ticker: str):
    return get_stock_info(ticker)

@app.get("/history/{ticker}")
def stock_history(ticker: str, period: str = "3mo"):
    return get_history(ticker, period)

@app.get("/indicators/{ticker}")
def stock_indicators(ticker: str):
    return get_indicators(ticker)