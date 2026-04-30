#  Crypto Trading Bot & Quant Dashboard

##  Overview

This project is a complete **algorithmic trading system** that integrates:

* Live crypto market data
* Trading strategy (EMA crossover)
* Backtesting engine
* Binance account integration
* Interactive dashboard

It is designed to simulate a **real-world quant trading workflow** including research, execution, and monitoring.

##  Strategy

The system uses a simple yet effective **EMA (Exponential Moving Average) crossover strategy**:

* **Buy Signal** → EMA(9) crosses above EMA(15)
* **Sell Signal** → EMA(9) crosses below EMA(15)
* **Risk Management** → Stop-loss implemented


##  Features

### 📊 Market Data

* Live BTC price tracking
* Historical OHLC data from Binance

###  Trading Bot

* Automated EMA-based signals
* Position tracking
* Logging system (`trading.log`)
* Stop-loss mechanism

### 🧪 Backtesting

* Strategy performance evaluation
* Simulated portfolio growth
* Capital-based trade execution

### 🏦 Account Integration

* Fetch real account balances via Binance API
* Secure API key handling using `.env`

### 📈 Dashboard

Built using streamlit

* Live price display
* Candlestick chart with EMAs
* Buy/Sell signals
* Account balances
* Backtest results
* Trade logs

---

##  Tech Stack

* Python
* Pandas
* Binance API
* Streamlit
* Plotly
* dotenv

---

## 📁 Project Structure

```
crypto-trading-bot/
│
├── dashboard_full.py        # Streamlit dashboard
├── trading_bot.py           # Live trading bot
├── backtest_ema.py          # Backtesting engine
├── price_tracker.py         # Live BTC price
├── balance.py               # Binance balance
│
├── trading.log              # Logs (auto-generated)
├── .env                     # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/crypto-trading-bot.git
cd crypto-trading-bot
```

### 2️⃣ Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3️⃣ Add API Keys

Create a `.env` file:

```
API_KEY=your_api_key
API_SECRET=your_api_secret
```

---

## ▶️ Usage

### Run Trading Bot

```bash
python3 trading_bot.py
```

### Run Dashboard

```bash
streamlit run dashboard_full.py
```

### Run Backtest

```bash
python3 backtest_ema.py
```

---

## 📊 Dashboard Preview

* Live BTC price
* EMA crossover signals
* Candlestick chart
* Account balances
* Strategy backtest
* Trade logs

---

## 🎯 Future Improvements

* Multi-asset portfolio trading
* Machine learning signals
* Risk-adjusted metrics (Sharpe ratio, drawdown)
* Portfolio optimization
* Cloud deployment

