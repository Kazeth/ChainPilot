# 🤖 Comprehensive AI Multi-Agent Crypto Trading System
## Sistema AI Multi-Agente para Sinais de Trading de Criptomoedas

### Deskripsi Sistem / System Description

Sistem AI Multi-Agent yang komprehensif untuk memberikan sinyal trading cryptocurrency dengan menggunakan:
- **Analisis Teknikal** (RSI, MACD, Bollinger Bands)
- **Analisis Sentimen** (Berita & Media Sosial)
- **Aktivitas Whale** (Transaksi On-chain)
- **Manajemen Risiko** (Stop Loss & Take Profit)

## 🏗️ Arsitektur Sistem / System Architecture

### 6 Agent Components:

1. **Technical Agent** (Port 8004)
   - Analisis RSI, MACD, Bollinger Bands
   - Data dari API Binance/KuCoin
   - Skor teknikal gabungan

2. **News Agent** (Port 8005)
   - Analisis sentimen berita crypto
   - Integrasi NewsAPI (opsional)
   - Scoring berdasarkan kata kunci

3. **Whale Agent** (Port 8006)
   - Monitoring transaksi whale (>$1M)
   - Data dari Whale Alert API (opsional)
   - Analisis aliran exchange

4. **Risk Manager Agent** (Port 8001)
   - Perhitungan Stop Loss & Take Profit
   - Berbasis ATR (Average True Range)
   - Manajemen ukuran posisi

5. **Comprehensive Signal Agent** (Port 8002)
   - Orchestrator semua analisis
   - Bobot: 40% teknikal, 30% sentimen, 30% whale
   - Generate sinyal akhir BUY/SELL/HOLD

6. **User Agent** (Port 8003)
   - Interface untuk pengguna
   - Tampilan sinyal yang komprehensif
   - Monitoring real-time

## 🚀 Panduan Instalasi / Installation Guide

### 1. Requirements

```bash
# Python 3.8 atau lebih tinggi
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Lingkungan / Environment Setup

```bash
# Clone atau download kode
cd /path/to/crypto-trading/

# Copy template konfigurasi
cp config_template.py config.py

# Edit konfigurasi sesuai kebutuhan
nano config.py  # atau editor lainnya
```

### 3. Konfigurasi API Keys (Opsional)

Edit file `config.py`:

```python
# NewsAPI (untuk data berita real-time)
NEWSAPI_CONFIG = {
    "api_key": "YOUR_NEWSAPI_KEY_HERE",  # https://newsapi.org
    "enabled": True,
}

# Whale Alert API (untuk data whale real-time)
WHALE_ALERT_CONFIG = {
    "api_key": "YOUR_WHALE_ALERT_KEY_HERE",  # https://whale-alert.io
    "enabled": True,
}
```

## 🏃 Cara Menjalankan Sistem / How to Run

### Opsi 1: Jalankan Semua Agent (Recommended)

```bash
# Jalankan semua 6 agent sekaligus
python run_all_agents.py

# Sistem akan menampilkan status semua agent dan mulai analisis
```

### Opsi 2: Jalankan Agent Individual

```bash
# Jalankan agent satu per satu (untuk debugging)
python run_all_agents.py --single-agent technical
python run_all_agents.py --single-agent news
python run_all_agents.py --single-agent whale
python run_all_agents.py --single-agent risk
python run_all_agents.py --single-agent signal
python run_all_agents.py --single-agent user
```

### Opsi 3: Manual Start (untuk Development)

```bash
# Terminal 1: Technical Agent
python technical_agent.py

# Terminal 2: News Agent  
python news_agent.py

# Terminal 3: Whale Agent
python whale_agent.py

# Terminal 4: Risk Manager
python enhanced_risk_manager_agent.py

# Terminal 5: Signal Orchestrator
python fixed_comprehensive_signal_agent.py

# Terminal 6: User Interface
python comprehensive_user_agent.py
```

## 🔧 Konfigurasi Agent Addresses

Setelah menjalankan sistem pertama kali, perbarui alamat agent:

### 1. Dapatkan Alamat Agent

Saat agent pertama kali berjalan, mereka akan menampilkan alamat seperti:
```
Technical Agent address: agent1qw7k9...
News Agent address: agent1qx8m2...
```

### 2. Update Konfigurasi

Edit file berikut dengan alamat yang benar:

**comprehensive_signal_agent.py:**
```python
TECHNICAL_AGENT_ADDRESS = "agent1qw7k9..."  # Alamat sebenarnya
NEWS_AGENT_ADDRESS = "agent1qx8m2..."      # Alamat sebenarnya
WHALE_AGENT_ADDRESS = "agent1qy9n3..."     # Alamat sebenarnya
RISK_MANAGER_ADDRESS = "agent1qz0o4..."    # Alamat sebenarnya
```

**comprehensive_user_agent.py:**
```python
SIGNAL_AGENT_ADDRESS = "agent1qa1p5..."    # Alamat sebenarnya
```

## 📊 Output Sistem / System Output

### Contoh Sinyal Trading:
```
================================================================================
📊 COMPREHENSIVE TRADING SIGNAL: BTCUSDT
================================================================================
🎯 FINAL SIGNAL: 🟢 BUY
🎲 CONFIDENCE:   78.5%
💰 PRICE:        $43,250.00
⏰ TIMESTAMP:    2024-01-15 10:30:00

📈 TECHNICAL ANALYSIS
----------------------------------------
RSI:              45.2
Technical Score:  🟢 [████████░░] +0.65
ATR:              0.0234

📰 SENTIMENT ANALYSIS
----------------------------------------
Sentiment Score:  🟢 [██████░░░░] +0.42
News Articles:    8
Top Headlines:
  1. Bitcoin shows strong bullish momentum amid institutional...
  2. Major whale accumulation detected in BTC markets...
  3. Technical indicators point to potential breakout...

🐋 WHALE ANALYSIS
----------------------------------------
Whale Score:      🟢 [████████░░] +0.73
Large Transactions: 12
Net Whale Flow:   $45,670,000
Flow Direction:   📈 Accumulating

⚖️ RISK MANAGEMENT
----------------------------------------
Take Profit:      $44,265.50
Stop Loss:        $42,234.50
Profit Potential: 2.35%
Risk Potential:   2.35%
Risk/Reward:      1.00:1

📋 ANALYSIS SUMMARY
----------------------------------------
Strong technical indicators with bullish RSI divergence. Positive news sentiment 
driven by institutional adoption. Significant whale accumulation detected.

📊 SUMMARY: 🟢 BTCUSDT | BUY | 🔥 78.5% confidence
================================================================================
```

## 🔄 Alur Komunikasi Agent / Agent Communication Flow

```
User Agent (8003)
    ↓ SignalRequest("BTCUSDT")
Comprehensive Signal Agent (8002)
    ↓ TechnicalRequest("BTCUSDT")     ↓ NewsRequest("BTCUSDT")        ↓ WhaleRequest("BTCUSDT")
Technical Agent (8004)              News Agent (8005)              Whale Agent (8006)
    ↓ TechnicalResponse                ↓ NewsResponse                  ↓ WhaleResponse
Comprehensive Signal Agent (8002)
    ↓ RiskRequest(signal_data)
Risk Manager Agent (8001)
    ↓ RiskResponse(tp_sl_data)
Comprehensive Signal Agent (8002)
    ↓ SignalResponse(comprehensive_data)
User Agent (8003) → Display to User
```

## 🛠️ Troubleshooting

### 1. Error: SSL Certificate Verification

```python
# Sudah ditangani dalam kode dengan:
requests.get(url, verify=False)
```

### 2. Error: Schema Digest Mismatch

```python
# Gunakan Protocol yang sama di semua agent:
Protocol("Signal Request v1")
```

### 3. Error: Agent Not Found

```bash
# Pastikan semua agent berjalan dan alamat sudah benar
# Cek log untuk alamat agent yang sebenarnya
```

### 4. Error: No API Response

```python
# Sistem menggunakan mock data sebagai fallback
# Periksa koneksi internet dan API keys
```

## 📋 Monitoring & Logging

### Log Files

```bash
# Setiap agent memiliki log sendiri
# Format: timestamp - agent_name - level - message

# Contoh log:
2024-01-15 10:30:15 - technical_agent - INFO - 📊 Calculating technical analysis for BTCUSDT
2024-01-15 10:30:16 - news_agent - INFO - 📰 Analyzing sentiment for 8 news articles
2024-01-15 10:30:17 - whale_agent - INFO - 🐋 Found 12 whale transactions in last 24h
```

### Performance Monitoring

```bash
# Monitor CPU dan Memory usage
htop

# Monitor network connections
netstat -tulpn | grep 800[1-6]

# Monitor log output
tail -f trading_system.log
```

## 🔒 Security & Best Practices

### 1. API Keys
- Jangan commit API keys ke version control
- Gunakan environment variables atau file config terpisah
- Rotasi API keys secara berkala

### 2. Network Security
- Agent berjalan di localhost secara default
- Untuk production, gunakan private network
- Implementasi authentication jika diperlukan

### 3. Risk Management
- Mulai dengan ukuran posisi kecil
- Set maximum risk per trade (default: 2%)
- Monitor performance secara real-time

## 📈 Customization & Extension

### 1. Menambah Trading Pairs

Edit `config.py`:
```python
TRADING_PAIRS = [
    "BTCUSDT",
    "ETHUSDT", 
    "ADAUSDT",  # Tambahkan pair baru
    "DOGEUSDT", # Tambahkan pair baru
]
```

### 2. Mengubah Parameter Teknikal

```python
TECHNICAL_SETTINGS = {
    "rsi_period": 21,        # Ubah periode RSI
    "rsi_overbought": 75,    # Ubah threshold overbought
    "rsi_oversold": 25,      # Ubah threshold oversold
}
```

### 3. Mengubah Bobot Sinyal

```python
SIGNAL_WEIGHTS = {
    "technical_weight": 0.50,    # 50% teknikal
    "sentiment_weight": 0.25,    # 25% sentimen  
    "whale_weight": 0.25,        # 25% whale
}
```

## 🆘 Support & Contact

Untuk pertanyaan atau masalah:
1. Periksa log files untuk error details
2. Pastikan semua dependencies terinstall
3. Verifikasi konfigurasi agent addresses
4. Test koneksi API secara manual

---

## 📝 Example Usage Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config_template.py config.py

# Run full system
python run_all_agents.py

# Monitor specific pair only
# Edit TRADING_PAIRS in config.py to ["BTCUSDT"]

# Stop system
# Press Ctrl+C in terminal
```

**Selamat trading! 🚀📈**
