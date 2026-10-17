import streamlit as st

from config import (
    CRYPTO_ASSETS,
    CUSTOM_LABEL,
    DEFAULT_FINNHUB_KEY,
    FINNHUB_ASSETS,
    FIXED_Q,
    FIXED_R,
    HTF_MAP,
    MARKET_CRYPTO,
    MARKET_FINNHUB,
    REVERSAL_PRESETS,
    TF_MAP_TV,
)


def _init_session_state():
    defaults = {
        "band_mult": 1.0,
        "vel_threshold": 0.01,
        "pivot_lookback": 14,
        "slope_mult": 1.0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_sidebar() -> dict:
    """วาด sidebar และคืนค่าการตั้งค่าทั้งหมดเป็น dict"""
    _init_session_state()

    st.sidebar.header("Data Source & Asset")
    market_type = st.sidebar.selectbox(
        "เลือกประเภทตลาด", [MARKET_CRYPTO, MARKET_FINNHUB]
    )

    finnhub_key = ""

    if market_type == MARKET_CRYPTO:
        selected_asset = st.sidebar.selectbox(
            "ค้นหาหรือเลือกสินทรัพย์ (Asset List)",
            options=list(CRYPTO_ASSETS.keys()),
            index=0,
        )
        if selected_asset == CUSTOM_LABEL:
            symbol_input = st.sidebar.text_input(
                "พิมพ์ชื่อ Symbol (Binance)", "LINKUSDT"
            ).upper()
        else:
            symbol_input = CRYPTO_ASSETS[selected_asset]
        tv_symbol = f"BINANCE:{symbol_input}"
        yf_symbol = symbol_input
    else:
        finnhub_key = st.sidebar.text_input(
            "ใส่ Finnhub API Key",
            value=DEFAULT_FINNHUB_KEY,
            type="password",
            help="รับ Key ฟรีที่ finnhub.io",
        )
        selected_asset = st.sidebar.selectbox(
            "ค้นหาหรือเลือกสินทรัพย์ (Asset List)",
            options=list(FINNHUB_ASSETS.keys()),
            index=0,
        )
        if selected_asset == CUSTOM_LABEL:
            custom_sym = st.sidebar.text_input(
                "พิมพ์ Finnhub Symbol (e.g. AMD, OANDA:EUR_USD)", "AMD"
            ).upper()
            symbol_input = tv_symbol = yf_symbol = custom_sym
        else:
            asset = FINNHUB_ASSETS[selected_asset]
            symbol_input = asset["fh"]
            tv_symbol = asset["tv"]
            yf_symbol = asset["yf"]

    st.sidebar.markdown("---")

    limit_input = st.sidebar.slider(
        "Historical Bars (Limit)",
        min_value=100, max_value=1000, value=500, step=100,
    )
    tf_input = st.sidebar.selectbox(
        "Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1
    )

    st.sidebar.header("Multi-Timeframe Filter")
    use_mtf_filter = st.sidebar.checkbox(
        "เปิดใช้งาน Multi-Timeframe Filter",
        value=False,
        help=(
            "เปิดเพื่อกรองเฉพาะสัญญาณที่ไปในทิศทางเดียวกับเทรนด์ภาพใหญ่"
            " ป้องกันการสวนเทรนด์แรงๆ"
        ),
    )
    htf_tf = HTF_MAP.get(tf_input, "1h")
    if use_mtf_filter:
        st.sidebar.info(f"กรองเทรนด์ภาพใหญ่จาก Timeframe: **{htf_tf}**")

    st.sidebar.header("Signal Engine Presets")
    if st.sidebar.button(
        f"โหลด Preset สัญญาณสำหรับ ({tf_input})", use_container_width=True
    ):
        p = REVERSAL_PRESETS.get(tf_input, REVERSAL_PRESETS["5m"])
        st.session_state.band_mult = p["band"]
        st.session_state.vel_threshold = p["threshold"]
        st.session_state.pivot_lookback = p["lookback"]
        st.session_state.slope_mult = p["slope_mult"]
        st.sidebar.success(f"โหลดค่า Preset สำหรับ {tf_input} เรียบร้อย!")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Signal Fine-Tuning")

    band_mult = st.sidebar.number_input(
        "Envelope Band Multiplier",
        min_value=0.2, max_value=5.0,
        value=st.session_state.band_mult, step=0.1,
        help=(
            "ยิ่งค่าน้อย: กรอบบีบแคบ สัญญาณเด้งไวและถี่ขึ้น แต่ข้อเสียคือมีโอกาสเจอสัญญาณหลอกสูงช่วง Sideways\n\n"
            "ยิ่งค่ามาก: กรองสัญญาณคมขึ้น ดักเฉพาะ Swing ใหญ่ แต่ข้อเสียคือสัญญาณออกช้าและน้อยลง"
        ),
    )
    vel_threshold = st.sidebar.number_input(
        "Velocity Threshold",
        min_value=0.000, max_value=5.000,
        value=st.session_state.vel_threshold, step=0.005, format="%.3f",
        help=(
            "ยิ่งค่าน้อย: ราคาขยับเปลี่ยนทิศนิดเดียวสัญญาณออกทันที สัญญาณถี่ ไวขึ้น แต่ข้อเสียคือแพ้ Noise ตลาดง่าย\n\n"
            "ยิ่งค่ามาก: ต้องใช้แรงซื้อ/ขายมหาศาลยืนยัน ชัวร์ขึ้น แต่ข้อเสียคือออกสัญญาณช้า ได้ต้นทุนไม่ดี"
        ),
    )
    pivot_lookback = st.sidebar.number_input(
        "Trendline Pivot Lookback",
        min_value=5, max_value=50,
        value=st.session_state.pivot_lookback, step=1,
        help=(
            "ยิ่งค่าน้อย: จับ Pivot โครงสร้างสั้น ตีเส้นเทรนด์ไลน์ไว สัญญาณ Breakout ออกถี่ แต่ข้อเสียคือเจอ Fake Break ง่าย\n\n"
            "ยิ่งค่ามาก: มองโครงสร้างใหญ่ เส้นเทรนด์ไลน์แข็งแกร่ง แม่นยำขึ้น แต่ข้อเสียคือสัญญาณ Breakout นานๆ เกิดที"
        ),
    )
    slope_mult = st.sidebar.number_input(
        "Trendline Slope Multiplier",
        min_value=0.1, max_value=5.0,
        value=st.session_state.slope_mult, step=0.1,
        help=(
            "ยิ่งค่าน้อย: เส้นเทรนด์ไลน์ชันน้อย เบรกง่าย สัญญาณมาเร็ว แต่ข้อเสียคือราคาโดนรบกวนนิดเดียวก็ออกสัญญาณหลอก\n\n"
            "ยิ่งค่ามาก: เส้นเทรนด์ไลน์ชันสูง ทะลุยาก กรองเฉพาะการพุ่งแรงจริงๆ แต่ข้อเสียคือเสียโอกาสจังหวะเบรกปกติ"
        ),
    )

    st.session_state.band_mult = band_mult
    st.session_state.vel_threshold = vel_threshold
    st.session_state.pivot_lookback = pivot_lookback
    st.session_state.slope_mult = slope_mult

    st.sidebar.info(f"**Kalman Status:** Baseline Q = {FIXED_Q}, R = {FIXED_R}")

    return {
        "market_type": market_type,
        "symbol_input": symbol_input,
        "tv_symbol": tv_symbol,
        "yf_symbol": yf_symbol,
        "finnhub_key": finnhub_key,
        "limit_input": limit_input,
        "tf_input": tf_input,
        "use_mtf_filter": use_mtf_filter,
        "htf_tf": htf_tf,
        "band_mult": band_mult,
        "vel_threshold": vel_threshold,
        "pivot_lookback": int(pivot_lookback),
        "slope_mult": slope_mult,
        "tv_interval": TF_MAP_TV.get(tf_input, "5"),
    }
