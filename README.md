# Kalman Filter for Trading

เว็บแดชบอร์ดแสดงกราฟราคาแบบเรียลไทม์ ที่ใช้ **ตัวกรองคาลมาน (Kalman Filter)** กรองสัญญาณรบกวนของราคา แล้วสร้างสัญญาณซื้อขาย BUY/SELL จากแถบ Envelope และเส้นแนวโน้ม (Trendline Breakout)

โครงงานวิชา 01076032 Elementary Differential Equations and Linear Algebra ปีการศึกษา 2569

## ความสามารถ
- รองรับคริปโตจาก Binance และหุ้นสหรัฐ ทองคำ Forex จาก Yahoo Finance / Finnhub
- เลือก Timeframe ได้ 1m, 5m, 15m, 1h, 1d และจำนวนแท่งย้อนหลัง 100–1,000 แท่ง
- เส้น Kalman Baseline และแถบ Envelope บน/ล่าง
- สัญญาณ BUY/SELL จากการกลับตัวที่ขอบแถบ และการ Breakout เส้นแนวโน้ม
- ตัวกรอง Multi-Timeframe กรองสัญญาณที่สวนทางกับเทรนด์ของ Timeframe ที่ใหญ่กว่า
- อัปเดตราคาแบบเรียลไทม์ผ่าน WebSocket พร้อมแท็บ TradingView Widget สำหรับเปรียบเทียบ

## แบบจำลองคณิตศาสตร์
ตัวกรองคาลมานแบบ 2 สถานะ ประมาณราคาและความเร็วของราคาไปพร้อมกัน

```text
เวกเตอร์สถานะ  x = [ราคา, ความเร็ว]ᵀ
A = [[1, 1], [0, 1]]    H = [1, 0]    Q = 0.1·I    R = 50    P₀ = 10·I

ทำนาย     x_pred = A·x               P_pred = A·P·Aᵀ + Q
ปรับปรุง   K = P_pred·Hᵀ·(H·P_pred·Hᵀ + R)⁻¹
          x = x_pred + K·(z − H·x_pred)
          P = (I − K·H)·P_pred
```

## โครงสร้างไฟล์
| ไฟล์ | หน้าที่ |
|---|---|
| `config.py` | ค่าคงที่ Q, R, ค่า Preset ของสัญญาณ และรายการสินทรัพย์ |
| `kalman_filter.py` | คลาส `NumPyKalmanFilter` คำนวณตัวกรองคาลมานด้วยเมทริกซ์ |
| `data_fetchers.py` | ดึงข้อมูลย้อนหลังจาก Binance และ yfinance |
| `sidebar.py` | แถบควบคุมสำหรับเลือกสินทรัพย์และปรับพารามิเตอร์ |
| `signals.py` | คำนวณแถบ Envelope, Trendline, Multi-Timeframe และสัญญาณ BUY/SELL |
| `charts.py` | กราฟ Lightweight Charts, WebSocket และ `updateKalman` ฝั่ง JavaScript |
| `app.py` | จุดเริ่มต้นของแอป รวมทุกส่วนเข้าด้วยกัน |

## วิธีติดตั้งและรัน
```bash
pip install -r requirements.txt
streamlit run app.py
```

ถ้าจะใช้ข้อมูลหุ้น ทองคำ หรือ Forex แบบเรียลไทม์ ให้กรอก Finnhub API Key ในแถบควบคุม หรือตั้งค่า Environment Variable ก่อนรัน

```powershell
$env:FINNHUB_API_KEY="your_key"   # Windows PowerShell
```
```bash
export FINNHUB_API_KEY="your_key"  # macOS / Linux
```

## สมาชิก
- นาย ธีรปรัชญ์ ตั้นพันธุ์ 68010544 
- นาย ธนภัทร แคล้วคลาด 68010467 
- นาย ศีตกานต์ แซ่ลิ่ม 68010125
- นาย ปัณณวิชญ์ กิติวงศ์ไพศาล 68010691

## หมายเหตุ
โปรแกรมนี้จัดทำเพื่อการศึกษาการประยุกต์ใช้พีชคณิตเชิงเส้นเท่านั้น สัญญาณซื้อขายไม่ใช่คำแนะนำการลงทุน