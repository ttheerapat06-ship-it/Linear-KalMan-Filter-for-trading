"""ดึงข้อมูลราคาย้อนหลัง Binance / yfinance (คนที่ 2)"""
import requests
import streamlit as st
import yfinance as yf

from config import MARKET_CRYPTO


@st.cache_data(ttl=60)
def fetch_binance_history(
    symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 500
):
    try:
        url = (
            "https://api.binance.com/api/v3/klines"
            f"?symbol={symbol}&interval={interval}&limit={limit}"
        )
        res = requests.get(url, timeout=5).json()
        return [
            {
                "time": int(c[0] / 1000),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
            }
            for c in res
        ]
    except Exception:
        return []


def _value(row, col):
    cell = row[col]
    return float(cell.iloc[0] if hasattr(cell, "iloc") else cell)


@st.cache_data(ttl=60)
def fetch_yfinance_history(
    symbol: str = "AAPL", interval: str = "1m", limit: int = 500
):
    try:
        period = "5d" if interval in ["1m", "5m", "15m"] else "1mo"
        data = yf.download(
            tickers=symbol, period=period, interval=interval, progress=False
        )
        if data.empty:
            return []

        candles = []
        for idx, row in data.iterrows():
            candles.append({
                "time": int(idx.timestamp()),
                "open": _value(row, "Open"),
                "high": _value(row, "High"),
                "low": _value(row, "Low"),
                "close": _value(row, "Close"),
            })
        return candles[-limit:]
    except Exception:
        return []


def load_history(
    market_type, symbol_input, yf_symbol, tf_input, htf_tf, limit, use_mtf
):
    """คืนค่า (historical_data, htf_data) ตามประเภทตลาด"""
    if market_type == MARKET_CRYPTO:
        historical = fetch_binance_history(symbol_input, tf_input, limit)
        htf = (
            fetch_binance_history(symbol_input, htf_tf, limit)
            if use_mtf
            else []
        )
    else:
        historical = fetch_yfinance_history(yf_symbol, tf_input, limit)
        htf = (
            fetch_yfinance_history(yf_symbol, htf_tf, limit)
            if use_mtf
            else []
        )
    return historical, htf
