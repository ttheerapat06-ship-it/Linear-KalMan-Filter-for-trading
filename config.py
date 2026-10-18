
import os

# อ่าน key จาก environment variable เท่านั้น ห้ามใส่ key จริงในโค้ด
DEFAULT_FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")

# ล็อกค่า Kalman Baseline คงที่ถาวร
FIXED_Q = 0.1
FIXED_R = 50.0

# จับคู่ Timeframe ปัจจุบัน กับ Higher Timeframe (HTF)
HTF_MAP = {
    "1m": "15m",
    "5m": "1h",
    "15m": "1h",
    "1h": "1d",
    "1d": "1d",
}

# Presets สำหรับความไวสัญญาณ
REVERSAL_PRESETS = {
    "1m": {"band": 0.8, "threshold": 0.00, "lookback": 10, "slope_mult": 1.0},
    "5m": {"band": 1.0, "threshold": 0.01, "lookback": 14, "slope_mult": 1.0},
    "15m": {"band": 1.1, "threshold": 0.01, "lookback": 14, "slope_mult": 1.0},
    "1h": {"band": 1.2, "threshold": 0.02, "lookback": 20, "slope_mult": 1.2},
    "1d": {"band": 1.2, "threshold": 0.02, "lookback": 20, "slope_mult": 1.2},
}

# Timeframe -> interval ของ TradingView
TF_MAP_TV = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "1d": "D"}

MARKET_CRYPTO = "Crypto (Binance WS)"
MARKET_FINNHUB = "US Stocks / Gold / Forex (Finnhub WS)"

CUSTOM_LABEL = "พิมพ์ Symbol อื่นๆ (Custom)..."

CRYPTO_ASSETS = {
    "BTCUSDT - Bitcoin": "BTCUSDT",
    "ETHUSDT - Ethereum": "ETHUSDT",
    "SOLUSDT - Solana": "SOLUSDT",
    "BNBUSDT - Binance Coin": "BNBUSDT",
    "XRPUSDT - Ripple": "XRPUSDT",
    "DOGEUSDT - Dogecoin": "DOGEUSDT",
    "ADAUSDT - Cardano": "ADAUSDT",
    "AVAXUSDT - Avalanche": "AVAXUSDT",
    "NEARUSDT - NEAR Protocol": "NEARUSDT",
    "SUIUSDT - Sui": "SUIUSDT",
    "PEPEUSDT - Pepe": "PEPEUSDT",
    "SHIBUSDT - Shiba Inu": "SHIBUSDT",
    CUSTOM_LABEL: "CUSTOM",
}

FINNHUB_ASSETS = {
    "AAPL - Apple Inc.": {"fh": "AAPL", "tv": "NASDAQ:AAPL", "yf": "AAPL"},
    "NVDA - Nvidia Corp.": {"fh": "NVDA", "tv": "NASDAQ:NVDA", "yf": "NVDA"},
    "TSLA - Tesla Inc.": {"fh": "TSLA", "tv": "NASDAQ:TSLA", "yf": "TSLA"},
    "MSFT - Microsoft Corp.": {"fh": "MSFT", "tv": "NASDAQ:MSFT", "yf": "MSFT"},
    "AMZN - Amazon.com Inc.": {"fh": "AMZN", "tv": "NASDAQ:AMZN", "yf": "AMZN"},
    "GOOGL - Alphabet Inc. (Google)": {
        "fh": "GOOGL", "tv": "NASDAQ:GOOGL", "yf": "GOOGL",
    },
    "META - Meta Platforms": {"fh": "META", "tv": "NASDAQ:META", "yf": "META"},
    "GLD - SPDR Gold ETF (ทองคำ)": {"fh": "GLD", "tv": "AMEX:GLD", "yf": "GLD"},
    "EUR/USD - Euro / US Dollar": {
        "fh": "OANDA:EUR_USD", "tv": "FX:EURUSD", "yf": "EURUSD=X",
    },
    "GBP/USD - British Pound / US Dollar": {
        "fh": "OANDA:GBP_USD", "tv": "FX:GBPUSD", "yf": "GBPUSD=X",
    },
    "USD/JPY - US Dollar / Japanese Yen": {
        "fh": "OANDA:USD_JPY", "tv": "FX:USDJPY", "yf": "JPY=X",
    },
    "BINANCE:BTCUSDT - Bitcoin (Finnhub Feed)": {
        "fh": "BINANCE:BTCUSDT", "tv": "BINANCE:BTCUSDT", "yf": "BTC-USD",
    },
    CUSTOM_LABEL: {"fh": "CUSTOM", "tv": "CUSTOM", "yf": "CUSTOM"},
}
