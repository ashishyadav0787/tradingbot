import pandas as pd
import time
import os
from dotenv import load_dotenv
from binance.client import Client
import streamlit as st

# ------------------ SETUP ------------------

try:
    API_KEY = st.secrets["API_KEY"]
    API_SECRET = st.secrets["API_SECRET"]
except:
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
INTERVAL = "1m"
TRADE_AMOUNT = 50
STOP_LOSS = 0.02
TAKE_PROFIT = 0.03

in_position = False
buy_price = 0
last_trade_index = -100

# ------------------ FILE PATH ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRADE_FILE = os.path.join(BASE_DIR, "trades.csv")

# ------------------ LOG TRADE ------------------

def log_trade(entry, exit_price, exit_type, market_type):
    pnl = exit_price - entry

    trade = pd.DataFrame([{
        "entry": entry,
        "exit": exit_price,
        "type": exit_type,
        "pnl": pnl,
        "market_type": market_type
    }])

    trade.to_csv(
        TRADE_FILE,
        mode='a',
        header=not os.path.exists(TRADE_FILE),
        index=False
    )

    print("✅ Trade saved")

# ------------------ RSI ------------------

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ------------------ DATA ------------------

def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=200)

    df = pd.DataFrame(klines, columns=[
        'time','open','high','low','close','volume',
        'close_time','qav','trades','taker_base','taker_quote','ignore'
    ])

    df['close'] = df['close'].astype(float)

    # EMA
    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema15'] = df['close'].ewm(span=15).mean()

    # RSI
    df['rsi'] = compute_rsi(df['close'])

    # Bollinger
    df['sma'] = df['close'].rolling(20).mean()
    df['std'] = df['close'].rolling(20).std()
    df['upper'] = df['sma'] + 2 * df['std']
    df['lower'] = df['sma'] - 2 * df['std']

    return df

# ------------------ STRATEGY ------------------

def strategy():
    global in_position, buy_price, last_trade_index

    df = get_data()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last['close']

    trend_strength = abs(last['ema9'] - last['ema15'])
    volatility = last['std']

    # ---------- MARKET TYPE ----------
    if trend_strength > 30:
        market_type = "TRENDING"
    else:
        market_type = "SIDEWAYS"

    # ---------- FILTERS ----------
    if volatility < df['std'].mean() * 0.5:
        return

    if len(df) - last_trade_index < 10:
        return

    # ---------- STRATEGY SWITCH ----------

    if market_type == "TRENDING":
        cross_up = prev['ema9'] < prev['ema15'] and last['ema9'] > last['ema15']
        trend_up = last['ema9'] > last['ema15']
        pullback = price <= last['ema9'] * 1.01

        buy_signal = trend_up and pullback and cross_up
        sell_signal = last['ema9'] < last['ema15']

    else:
        buy_signal = price < last['lower'] and last['rsi'] < 30
        sell_signal = price > last['upper']

    # ---------- BUY ----------
    if not in_position and buy_signal:
        print(f"🟢 BUY at {price}")
        in_position = True
        buy_price = price
        last_trade_index = len(df)

    # ---------- SELL ----------
    if in_position:
        stop_loss = price < buy_price * (1 - STOP_LOSS)
        take_profit = price > buy_price * (1 + TAKE_PROFIT)

        if sell_signal or stop_loss or take_profit:
            print(f"🔴 SELL at {price}")

            reason = "SIGNAL"
            if stop_loss:
                reason = "STOP LOSS"
            elif take_profit:
                reason = "TAKE PROFIT"

            log_trade(buy_price, price, reason, market_type)

            in_position = False
            last_trade_index = len(df)

    print(f"Price: {price:.2f} | Market: {market_type}")

# ------------------ MAIN LOOP ------------------

print("🚀 Smart Bot Started...")

while True:
    try:
        strategy()
        time.sleep(5)
    except Exception as e:
        print("Error:", e)
        time.sleep(10)