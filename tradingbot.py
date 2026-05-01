import pandas as pd
import time
import os
from dotenv import load_dotenv
from binance.client import Client
import logging

# ------------------ SETUP ------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
INTERVAL = "1m"
TRADE_AMOUNT = 50
STOP_LOSS = 0.02

in_position = False
buy_price = 0

# ------------------ FILE PATH ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRADE_FILE = os.path.join(BASE_DIR, "trades.csv")

# ------------------ LOG TRADE ------------------
def log_trade(entry, exit_price, exit_type):
    pnl = exit_price - entry

    trade = pd.DataFrame([{
        "entry": entry,
        "exit": exit_price,
        "type": exit_type,
        "pnl": pnl
    }])

    file_exists = os.path.exists(TRADE_FILE)

    trade.to_csv(
        TRADE_FILE,
        mode='a',
        header=not file_exists,
        index=False
    )

    print("✅ Trade saved")

# ------------------ DATA ------------------
def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=100)

    df = pd.DataFrame(klines)
    df[4] = df[4].astype(float)

    df['ema9'] = df[4].ewm(span=9).mean()
    df['ema15'] = df[4].ewm(span=15).mean()

    return df

# ------------------ BUY ------------------
def buy(price):
    global in_position, buy_price

    print(f"🟢 BUY at {price}")
    in_position = True
    buy_price = price

# ------------------ SELL ------------------
def sell(price, reason="SIGNAL"):
    global in_position, buy_price

    print(f"🔴 SELL at {price} ({reason})")

    # 🔥 LOG TRADE (MOST IMPORTANT)
    log_trade(buy_price, price, reason)

    in_position = False

# ------------------ STRATEGY ------------------
def strategy():
    global in_position, buy_price

    df = get_data()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last[4]

    # BUY SIGNAL
    if prev['ema9'] < prev['ema15'] and last['ema9'] > last['ema15']:
        if not in_position:
            buy(price)

    # SELL SIGNAL
    elif prev['ema9'] > prev['ema15'] and last['ema9'] < last['ema15']:
        if in_position:
            sell(price, "CROSSOVER")

    # STOP LOSS
    if in_position and price < buy_price * (1 - STOP_LOSS):
        sell(price, "STOP LOSS")

    print(f"Price: {price:.2f}")

# ------------------ MAIN LOOP ------------------
print("🚀 Bot Started...")

while True:
    try:
        strategy()
        time.sleep(5)
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
