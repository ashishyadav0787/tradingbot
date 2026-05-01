🚀 TradingBot — Algorithmic Crypto Trading System

A Python-based algorithmic trading system that combines multiple technical strategies, real-time data processing, and interactive dashboards for cryptocurrency trading.

This project demonstrates strategy design, backtesting, and visualization using live market data from Binance.

📌 Features
📊 Multi-Strategy Trading System
EMA Crossover (Trend Following)
RSI Momentum Filter
Bollinger Bands (Mean Reversion)

🤖 Smart Market Detection
Automatically identifies:
TRENDING market → uses EMA strategy
SIDEWAYS market → uses Bollinger strategy

📉 Backtesting Engine
Simulates trades on historical data
Calculates:
PnL (Profit & Loss)
Win Rate
Trade History

📈 Interactive Dashboard (Streamlit)
Live BTC price tracking
Trade visualization with BUY/SELL signals
Strategy performance metrics
Candlestick charts with indicators

⚙️ Risk Management
Stop Loss
Take Profit
Cooldown period (prevents overtrading)
Volatility filter

🧠 Strategy Logic
📈 Trending Market (EMA + RSI)
EMA(9) crosses above EMA(15)
Price near EMA (pullback entry)
Avoid overbought zones

📊 Sideways Market (Bollinger Bands)
Buy when price touches lower band
RSI confirms oversold (<30)
Sell at upper band

🏗️ Project Structure
tradingbot/
│
├── tradingbot.py        # Live trading logic (simulation)
├── backtest_ema.py      # Backtesting engine
├── dashboard_full.py    # Streamlit dashboard
├── trades.csv           # Trade logs
├── requirements.txt
└── README.md

⚡ Installation
1. Clone the repository
git clone https://github.com/ashishyadav0787/tradingbot.git
cd tradingbot
2. Install dependencies
pip install -r requirements.txt
3. Add API Keys
🔹 Option 1 (Local)

Create .env:

API_KEY=your_api_key
API_SECRET=your_secret
🔹 Option 2 (Streamlit Cloud)

Create .streamlit/secrets.toml:

API_KEY="your_api_key"
API_SECRET="your_secret"

🚀 Usage
▶️ Run Trading Bot
python tradingbot.py

📊 Run Dashboard
streamlit run dashboard_full.py

🧪 Run Backtest
python backtest_ema.py

📊 Example Output
Final Balance
Total Trades
Win Rate
Trade History
