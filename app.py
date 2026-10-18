"""จุดเริ่มต้นของแอป: รวมทุกโมดูลเข้าด้วยกัน (คนที่ 4)

รัน: streamlit run app.py
"""
import streamlit as st
import streamlit.components.v1 as components

from charts import (
    build_custom_chart_html,
    build_js_websocket,
    build_tradingview_html,
)
from config import MARKET_CRYPTO
from data_fetchers import load_history
from sidebar import render_sidebar
from signals import compute_signals

st.set_page_config(
    page_title="Real-Time Multi-Asset Kalman Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("KALMAN FILTER FOR TRADING")

cfg = render_sidebar()

historical_data, htf_data = load_history(
    cfg["market_type"],
    cfg["symbol_input"],
    cfg["yf_symbol"],
    cfg["tf_input"],
    cfg["htf_tf"],
    cfg["limit_input"],
    cfg["use_mtf_filter"],
)

if historical_data:
    result = compute_signals(
        historical_data,
        htf_data,
        cfg["use_mtf_filter"],
        cfg["band_mult"],
        cfg["vel_threshold"],
        cfg["pivot_lookback"],
        cfg["slope_mult"],
    )

    js_websocket = build_js_websocket(
        cfg["market_type"],
        cfg["symbol_input"],
        cfg["tf_input"],
        cfg["finnhub_key"],
        cfg["vel_threshold"],
        cfg["band_mult"],
        result["std_dev"],
        cfg["use_mtf_filter"],
        result["current_htf_trend"],
    )
    custom_chart_html = build_custom_chart_html(
        historical_data, result, js_websocket
    )
    tradingview_html = build_tradingview_html(
        cfg["tv_symbol"], cfg["tv_interval"]
    )

    tab1, tab2 = st.tabs(
        ["Custom Kalman Chart (Real-time)", "Official TradingView Widget"]
    )

    with tab1:
        if cfg["market_type"] != MARKET_CRYPTO and not cfg["finnhub_key"]:
            st.warning(
                "กรุณากรอก Finnhub API Key ใน Sidebar เพื่อเปิดใช้งาน Real-Time"
                " WebSocket สำหรับหุ้น/สินทรัพย์ทั่วไป"
            )
        components.html(custom_chart_html, height=640)

    with tab2:
        components.html(tradingview_html, height=670)
else:
    st.error(
        f"ไม่สามารถดึงข้อมูลของ '{cfg['symbol_input']}' ได้"
        " โปรดตรวจสอบชื่อ Symbol"
    )
