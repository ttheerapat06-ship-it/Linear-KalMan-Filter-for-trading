import numpy as np

from config import FIXED_Q, FIXED_R
from kalman_filter import NumPyKalmanFilter

GREEN = "#10B981"
RED = "#EF4444"

def compute_htf_trend(htf_data, use_mtf_filter):
    """คืนค่า (htf_trend_map, current_htf_trend)"""
    htf_trend_map = {}
    current_htf_trend = "UP"

    if use_mtf_filter and htf_data:
        engine = NumPyKalmanFilter(
            q_var=FIXED_Q, r_var=FIXED_R, initial_price=htf_data[0]["close"]
        )
        for candle in htf_data:
            kp, _ = engine.update(candle["close"])
            htf_trend_map[candle["time"]] = (
                "UP" if candle["close"] >= kp else "DOWN"
            )
        current_htf_trend = htf_trend_map[sorted(htf_trend_map.keys())[-1]]

    return htf_trend_map, current_htf_trend

def _make_htf_lookup(htf_trend_map, use_mtf_filter):
    def get_htf_trend_at(ts):
        if not use_mtf_filter or not htf_trend_map:
            return "BOTH"
        valid_times = [t for t in htf_trend_map if t <= ts]
        if valid_times:
            return htf_trend_map[max(valid_times)]
        return "BOTH"

    return get_htf_trend_at

def compute_signals(
    historical_data,
    htf_data,
    use_mtf_filter,
    band_mult,
    vel_threshold,
    pivot_lookback,
    slope_mult,
):
    """คำนวณเส้น Kalman, Envelope และ markers BUY/SELL ทั้งหมด"""
    htf_trend_map, current_htf_trend = compute_htf_trend(
        htf_data, use_mtf_filter
    )
    get_htf_trend_at = _make_htf_lookup(htf_trend_map, use_mtf_filter)

    # --- ผ่านที่ 1: หา std_dev ของ (ราคา - Kalman) ---
    engine = NumPyKalmanFilter(
        q_var=FIXED_Q, r_var=FIXED_R, initial_price=historical_data[0]["close"]
    )
    raw_kalman_prices = [engine.update(c["close"])[0] for c in historical_data]
    prices = np.array([c["close"] for c in historical_data])
    highs = np.array([c["high"] for c in historical_data])
    lows = np.array([c["low"] for c in historical_data])

    diffs = [p - k for p, k in zip(prices, raw_kalman_prices)]
    std_dev = float(np.std(diffs)) if len(diffs) > 0 else 1.0

    # --- ATR และ slope สำหรับ Trendline Breakout (LuxAlgo style) ---
    lookback = pivot_lookback
    tr = np.maximum(
        highs[1:] - lows[1:],
        np.maximum(
            np.abs(highs[1:] - prices[:-1]), np.abs(lows[1:] - prices[:-1])
        ),
    )
    atr = float(np.mean(tr[-lookback:])) if len(tr) >= lookback else 1.0
    slope = (atr / lookback) * slope_mult

    # --- ผ่านที่ 2: สร้างเส้นและสัญญาณ ---
    engine = NumPyKalmanFilter(
        q_var=FIXED_Q, r_var=FIXED_R, initial_price=historical_data[0]["close"]
    )
    kalman_line, upper_band, lower_band, markers = [], [], [], []

    slope_ph, slope_pl = slope, slope
    upper_tl, lower_tl = prices[0], prices[0]
    upos, dnos = 0, 0
    prev_upos, prev_dnos = 0, 0

    for i, c in enumerate(historical_data):
        kp, kv = engine.update(c["close"])

        upper_b = kp + (std_dev * band_mult)
        lower_b = kp - (std_dev * band_mult)

        kalman_line.append({"time": c["time"], "value": kp})
        upper_band.append({"time": c["time"], "value": upper_b})
        lower_band.append({"time": c["time"], "value": lower_b})

        if i >= lookback * 2:
            window_highs = highs[i - (lookback * 2): i + 1]
            window_lows = lows[i - (lookback * 2): i + 1]

            is_ph = highs[i - lookback] == np.max(window_highs)
            is_pl = lows[i - lookback] == np.min(window_lows)

            if is_ph:
                slope_ph = slope
                upper_tl = highs[i - lookback]
            else:
                upper_tl -= slope_ph

            if is_pl:
                slope_pl = slope
                lower_tl = lows[i - lookback]
            else:
                lower_tl += slope_pl

            upos = 0 if is_ph else (1 if c["close"] > upper_tl else upos)
            dnos = 0 if is_pl else (1 if c["close"] < lower_tl else dnos)

        if i > 0:
            prev_c = historical_data[i - 1]
            htf_state = get_htf_trend_at(c["time"])

            is_bottom_reversal = (
                prev_c["close"] <= lower_b or c["low"] <= lower_b
            ) and (c["close"] > prev_c["high"])
            is_top_reversal = (
                prev_c["close"] >= upper_b or c["high"] >= upper_b
            ) and (c["close"] < prev_c["low"])

            is_trendline_buy = upos > prev_upos
            is_trendline_sell = dnos > prev_dnos

            buy_condition = (
                (is_bottom_reversal or is_trendline_buy)
                and (kv > -vel_threshold)
                and (htf_state in ["UP", "BOTH"])
            )
            sell_condition = (
                (is_top_reversal or is_trendline_sell)
                and (kv < vel_threshold)
                and (htf_state in ["DOWN", "BOTH"])
            )

            if buy_condition:
                markers.append({
                    "time": c["time"],
                    "position": "belowBar",
                    "color": GREEN,
                    "shape": "arrowUp",
                    "text": "BUY (Breakout)" if is_trendline_buy else "BUY",
                })
            elif sell_condition:
                markers.append({
                    "time": c["time"],
                    "position": "aboveBar",
                    "color": RED,
                    "shape": "arrowDown",
                    "text": "SELL (Breakout)" if is_trendline_sell else "SELL",
                })

        prev_upos = upos
        prev_dnos = dnos

    return {
        "kalman_line_data": kalman_line,
        "upper_band_data": upper_band,
        "lower_band_data": lower_band,
        "markers": markers,
        "std_dev": std_dev,
        "current_htf_trend": current_htf_trend,
        # state สุดท้าย ส่งต่อให้ JS คำนวณ real-time ต่อจากเดิม
        "kalman_state": {
            "x_price": float(engine.x[0, 0]),
            "x_vel": float(engine.x[1, 0]),
            "P11": float(engine.P[0, 0]),
            "P12": float(engine.P[0, 1]),
            "P21": float(engine.P[1, 0]),
            "P22": float(engine.P[1, 1]),
        },
    }
