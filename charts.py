"""Frontend: HTML/JS ของกราฟ Real-time และ TradingView widget (คนที่ 4)"""
import json

from config import FIXED_Q, FIXED_R, MARKET_CRYPTO


def build_js_websocket(
    market_type,
    symbol_input,
    tf_input,
    finnhub_key,
    vel_threshold,
    band_mult,
    std_dev,
    use_mtf_filter,
    current_htf_trend,
):
    """สร้างโค้ด JS ของ WebSocket (Binance หรือ Finnhub)"""
    ws_symbol = symbol_input.lower()
    mtf_filter_js = "true" if use_mtf_filter else "false"

    if market_type == MARKET_CRYPTO:
        return f"""
            const velThreshold = {vel_threshold};
            const bandMult = {band_mult};
            const stdDev = {std_dev};
            const useMtf = {mtf_filter_js};
            const currentHtfTrend = "{current_htf_trend}";

            const socket = new WebSocket('wss://stream.binance.com:9443/ws/{ws_symbol}@kline_{tf_input}');
            socket.onmessage = function(event) {{
                const message = JSON.parse(event.data);
                const kline = message.k;

                const time = Math.floor(kline.t / 1000);
                const open = parseFloat(kline.o);
                const high = parseFloat(kline.h);
                const low = parseFloat(kline.l);
                const close = parseFloat(kline.c);

                candlestickSeries.update({{ time, open, high, low, close }});

                let prevVel = x_vel;
                const kalmanRes = updateKalman(close);

                const upperBand = kalmanRes.price + (stdDev * bandMult);
                const lowerBand = kalmanRes.price - (stdDev * bandMult);

                kalmanLineSeries.update({{ time: time, value: kalmanRes.price }});
                upperSeries.update({{ time: time, value: upperBand }});
                lowerSeries.update({{ time: time, value: lowerBand }});

                let newSignal = null;
                const len = historyCandles.length;
                if (len > 0) {{
                    const prevC = historyCandles[len - 1];
                    const isBottomReversal = (prevC.close <= lowerBand || low <= lowerBand) && (close > prevC.high);
                    const isTopReversal = (prevC.close >= upperBand || high >= upperBand) && (close < prevC.low);

                    const allowBuy = !useMtf || currentHtfTrend === "UP";
                    const allowSell = !useMtf || currentHtfTrend === "DOWN";

                    if (isBottomReversal && kalmanRes.velocity > -velThreshold && allowBuy) {{
                        newSignal = {{ time: time, position: 'belowBar', color: '#10B981', shape: 'arrowUp', text: 'BUY' }};
                    }} else if (isTopReversal && kalmanRes.velocity < velThreshold && allowSell) {{
                        newSignal = {{ time: time, position: 'aboveBar', color: '#EF4444', shape: 'arrowDown', text: 'SELL' }};
                    }}
                }}

                if (newSignal) {{
                    markers = markers.filter(m => m.time !== time);
                    markers.push(newSignal);
                    markers.sort((a, b) => a.time - b.time);
                    candlestickSeries.setMarkers(markers);
                }}
            }};
        """

    return f"""
            const velThreshold = {vel_threshold};
            const bandMult = {band_mult};
            const stdDev = {std_dev};
            const useMtf = {mtf_filter_js};
            const currentHtfTrend = "{current_htf_trend}";

            const socket = new WebSocket('wss://ws.finnhub.io?token={finnhub_key}');

            socket.addEventListener('open', function (event) {{
                socket.send(JSON.stringify({{'type':'subscribe', 'symbol': '{symbol_input}'}}));
            }});

            let lastCandle = historyCandles.length > 0 ? historyCandles[historyCandles.length - 1] : null;

            socket.addEventListener('message', function (event) {{
                const msg = JSON.parse(event.data);
                if (msg.type === 'trade' && msg.data && msg.data.length > 0) {{
                    const trade = msg.data[msg.data.length - 1];
                    const price = parseFloat(trade.p);
                    if (isNaN(price) || price <= 0) return;

                    const rawTimestamp = trade.t ? Math.floor(trade.t / 1000) : Math.floor(Date.now() / 1000);
                    const candleTime = Math.floor(rawTimestamp / 60) * 60;

                    if (!lastCandle || candleTime > lastCandle.time) {{
                        lastCandle = {{
                            time: candleTime,
                            open: price,
                            high: price,
                            low: price,
                            close: price
                        }};
                    }} else {{
                        lastCandle.high = Math.max(lastCandle.high, price);
                        lastCandle.low = Math.min(lastCandle.low, price);
                        lastCandle.close = price;
                    }}

                    candlestickSeries.update(lastCandle);

                    let prevVel = x_vel;
                    const kalmanRes = updateKalman(price);

                    const upperBand = kalmanRes.price + (stdDev * bandMult);
                    const lowerBand = kalmanRes.price - (stdDev * bandMult);

                    kalmanLineSeries.update({{ time: lastCandle.time, value: kalmanRes.price }});
                    upperSeries.update({{ time: lastCandle.time, value: upperBand }});
                    lowerSeries.update({{ time: lastCandle.time, value: lowerBand }});

                    let newSignal = null;
                    const len = historyCandles.length;
                    if (len > 1) {{
                        const prevC = historyCandles[len - 2];
                        const isBottomReversal = (prevC.close <= lowerBand || lastCandle.low <= lowerBand) && (lastCandle.close > prevC.high);
                        const isTopReversal = (prevC.close >= upperBand || lastCandle.high >= upperBand) && (lastCandle.close < prevC.low);

                        const allowBuy = !useMtf || currentHtfTrend === "UP";
                        const allowSell = !useMtf || currentHtfTrend === "DOWN";

                        if (isBottomReversal && kalmanRes.velocity > -velThreshold && allowBuy) {{
                            newSignal = {{ time: lastCandle.time, position: 'belowBar', color: '#10B981', shape: 'arrowUp', text: 'BUY' }};
                        }} else if (isTopReversal && kalmanRes.velocity < velThreshold && allowSell) {{
                            newSignal = {{ time: lastCandle.time, position: 'aboveBar', color: '#EF4444', shape: 'arrowDown', text: 'SELL' }};
                        }}
                    }}

                    if (newSignal) {{
                        markers = markers.filter(m => m.time !== lastCandle.time);
                        markers.push(newSignal);
                        markers.sort((a, b) => a.time - b.time);
                        candlestickSeries.setMarkers(markers);
                    }}
                }}
            }});
        """


def build_custom_chart_html(historical_data, signal_result, js_websocket):
    """สร้าง HTML ของกราฟ Lightweight Charts"""
    ks = signal_result["kalman_state"]
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/lightweight-charts@3.8.0/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: #111827; }}
            #chart {{ width: 100%; height: 620px; }}
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            const historyCandles = {json.dumps(historical_data)};
            const historyKalman = {json.dumps(signal_result["kalman_line_data"])};
            const historyUpper = {json.dumps(signal_result["upper_band_data"])};
            const historyLower = {json.dumps(signal_result["lower_band_data"])};

            let markers = {json.dumps(signal_result["markers"])};

            let precision = 2;
            let minMove = 0.01;
            if (historyCandles.length > 0) {{
                const samplePrice = historyCandles[0].close;
                if (samplePrice < 2) {{
                    precision = 5;
                    minMove = 0.00001;
                }} else if (samplePrice < 500) {{
                    precision = 3;
                    minMove = 0.001;
                }}
            }}

            const chartElement = document.getElementById('chart');
            const chart = LightweightCharts.createChart(chartElement, {{
                width: chartElement.clientWidth,
                height: 620,
                layout: {{ backgroundColor: '#111827', textColor: '#D1D5DB' }},
                grid: {{ vertLines: {{ color: '#1F2937' }}, horzLines: {{ color: '#1F2937' }} }},
                timeScale: {{ timeVisible: true, secondsVisible: true }}
            }});

            const candlestickSeries = chart.addCandlestickSeries({{
                upColor: '#10B981', downColor: '#EF4444', borderVisible: false, wickUpColor: '#10B981', wickDownColor: '#EF4444',
                priceFormat: {{ type: 'price', precision: precision, minMove: minMove }}
            }});

            const kalmanLineSeries = chart.addLineSeries({{
                color: '#3B82F6',
                lineWidth: 3,
                title: 'Kalman Baseline',
                priceFormat: {{ type: 'price', precision: precision, minMove: minMove }}
            }});

            const upperSeries = chart.addLineSeries({{
                color: 'rgba(239, 68, 68, 0.4)',
                lineWidth: 3,
                lineStyle: 0,
                title: 'Upper Envelope',
                priceFormat: {{ type: 'price', precision: precision, minMove: minMove }}
            }});

            const lowerSeries = chart.addLineSeries({{
                color: 'rgba(16, 185, 129, 0.4)',
                lineWidth: 3,
                lineStyle: 0,
                title: 'Lower Envelope',
                priceFormat: {{ type: 'price', precision: precision, minMove: minMove }}
            }});

            candlestickSeries.setData(historyCandles);
            kalmanLineSeries.setData(historyKalman);
            upperSeries.setData(historyUpper);
            lowerSeries.setData(historyLower);

            candlestickSeries.setMarkers(markers);

            let x_price = {ks["x_price"]};
            let x_vel = {ks["x_vel"]};
            let P11 = {ks["P11"]};
            let P12 = {ks["P12"]};
            let P21 = {ks["P21"]};
            let P22 = {ks["P22"]};
            const Q = {FIXED_Q};
            const R = {FIXED_R};

            function updateKalman(z) {{
                let x_price_pred = x_price + x_vel;
                let x_vel_pred = x_vel;

                let P11_pred = P11 + P12 + P21 + P22 + Q;
                let P12_pred = P12 + P22;
                let P21_pred = P21 + P22;
                let P22_pred = P22 + Q;

                let S = P11_pred + R;
                let K1 = P11_pred / S;
                let K2 = P21_pred / S;

                let y = z - x_price_pred;

                x_price = x_price_pred + K1 * y;
                x_vel = x_vel_pred + K2 * y;

                P11 = (1.0 - K1) * P11_pred;
                P12 = (1.0 - K1) * P12_pred;
                P21 = P21_pred - K2 * P11_pred;
                P22 = P22_pred - K2 * P12_pred;

                return {{ price: x_price, velocity: x_vel }};
            }}

            {js_websocket}

            window.addEventListener('resize', () => {{
                chart.resize(chartElement.clientWidth, 620);
            }});
        </script>
    </body>
    </html>
    """


def build_tradingview_html(tv_symbol, tv_interval):
    """สร้าง HTML ของ TradingView widget"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: #111827; }}
            .tradingview-widget-container {{ width: 100%; height: 650px; }}
        </style>
    </head>
    <body>
        <div class="tradingview-widget-container">
            <div id="tradingview_advanced_chart" style="height: 100%; width: 100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
                new TradingView.widget({{
                    "autosize": true,
                    "symbol": "{tv_symbol}",
                    "interval": "{tv_interval}",
                    "timezone": "Asia/Bangkok",
                    "theme": "dark",
                    "style": "1",
                    "locale": "th",
                    "toolbar_bg": "#1F2937",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "hide_top_toolbar": false,
                    "allow_symbol_change": true,
                    "save_image": true,
                    "details": true,
                    "container_id": "tradingview_advanced_chart"
                }});
            </script>
        </div>
    </body>
    </html>
    """
