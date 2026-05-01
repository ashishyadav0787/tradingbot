import pandas as pd
from binance.client import Client
import numpy as np
import streamlit as st
import os 

API_KEY = st.secrets["API_KEY"]
API_SECRET = st.secrets["API_SECRET"]
client = Client(API_KEY, API_SECRET)

# Fetch BTC data
klines = client.get_klines(symbol="BTCUSDT", interval="1h", limit=500)

df = pd.DataFrame(klines, columns=[
    'time','open','high','low','close','volume',
    'close_time','qav','trades','taker_base','taker_quote','ignore'
])


#  RSI 
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


#  PREP DATA 
df['close'] = df['close'].astype(float)
df['time'] = pd.to_datetime(df['time'], unit='ms')  
df['ema9'] = df['close'].ewm(span=9).mean()
df['ema15'] = df['close'].ewm(span=15).mean()
df['rsi'] = compute_rsi(df['close'])
df['sma'] = df['close'].rolling(20).mean()
df['std'] = df['close'].rolling(20).std()
df['upper'] = df['sma'] + 2 * df['std']
df['lower'] = df['sma'] - 2 * df['std']

strategy = "EMA + RSI"   # change to "Bollinger"

#  PARAMS 
INITIAL_BAL = 1000
SL = 0.02
FEE = 0.001

balance = INITIAL_BAL
position = 0.0
entry_price = 0.0
entry_time = None

trades = []

TREND_MIN = 20        # tune based on timeframe
COOLDOWN = 10         # candles to wait
USE_VOL_FILTER = True
VOL_MIN = df['std'].mean() * 0.5  # simple baseline
last_trade_index = -100

TREND_THRESHOLD = 30   # tune this

# ------------------ BACKTEST LOOP ------------------

for i in range(20, len(df)-1):
    price = df['close'][i]
    next_price = df['close'][i+1]
    next_time = df['time'][i+1]

    trend_strength = abs(df['ema9'][i] - df['ema15'][i])
    volatility = df['std'][i]

    # ---------- AUTO MARKET DETECTION ----------
    if trend_strength > TREND_THRESHOLD:
        market_type = "TRENDING"
    else:
        market_type = "SIDEWAYS"

    # ---------- COOLDOWN ----------
    if i - last_trade_index < COOLDOWN:
        continue

    # ---------- STRATEGY SWITCH ----------
    if market_type == "TRENDING":
        cross_up = df['ema9'][i] > df['ema15'][i] and df['ema9'][i-1] <= df['ema15'][i-1]
        trend_up = df['ema9'][i] > df['ema15'][i]
        pullback = price <= df['ema9'][i] * 1.01

        buy_condition = trend_up and pullback and cross_up
        sell_condition = df['ema9'][i] < df['ema15'][i]

    else:  # SIDEWAYS → Bollinger
        buy_condition = price < df['lower'][i] and df['rsi'][i] < 30
        sell_condition = price > df['upper'][i]

    # ---------- BUY ----------
    if position == 0 and buy_condition:
        position = (balance / next_price) * (1 - FEE)
        entry_price = next_price
        entry_time = next_time
        balance = 0
        last_trade_index = i

    # ---------- SELL ----------
    if position > 0:
        stop_loss = price < entry_price * (1 - SL)
        take_profit = price > entry_price * (1 + TP)

        if sell_condition or stop_loss or take_profit:
            exit_price = next_price
            exit_time = next_time

            balance = position * exit_price * (1 - FEE)

            pnl = (exit_price - entry_price) * position

            trades.append({
                "entry_time": entry_time,
                "exit_time": exit_time,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "market_type": market_type
            })

            position = 0
            last_trade_index = i
# ------------------ RESULTS ------------------

final_value = balance if position == 0 else position * df['close'].iloc[-1]

trades_df = pd.DataFrame(trades)

print("Final Balance:", round(final_value, 2))
print("Total Trades:", len(trades_df))

if not trades_df.empty:
    print("Total PnL:", round(trades_df['pnl'].sum(), 2))
    print("Win Rate:", round((trades_df['pnl'] > 0).mean() * 100, 2), "%")
    print(trades_df.tail())