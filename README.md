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

🚀 Usage
▶️ Run Trading Bot
python tradingbot.py

📊 Run Dashboard
streamlit run app.py

🧪 Run Backtest
python backtest_ema.py

📊 Example Output
Final Balance
Total Trades
Win Rate
Trade History
