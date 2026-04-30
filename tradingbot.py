import pandas as pd
import time
import streamlit as st
import os
from dotenv import load_dotenv
from binance.client import Client
import logging

# - SETUP -
try:
    API_KEY = st.secrets["API_KEY"]
    API_SECRET = st.secrets["API_SECRET"]
except:
    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
INTERVAL = "5m"
TRADE_AMOUNT = 50   # USDT
STOP_LOSS = 0.02    # 2%

in_position = False
buy_price = 0

# - LOGGING -
logging.basicConfig(
    filename="trading.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# - FUNCTIONS -

def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=100)

    df = pd.DataFrame(klines)
    df[4] = df[4].astype(float)

    df['ema9'] = df[4].ewm(span=9).mean()
    df['ema15'] = df[4].ewm(span=15).mean()

    return df

def buy(price):
    global in_position, buy_price

    qty = round(TRADE_AMOUNT / price, 5)

    print(f"BUY at {price}")
    logging.info(f"BUY at {price}")

    # Uncomment for real trade
    # client.order_market_buy(symbol=SYMBOL, quantity=qty)

    in_position = True
    buy_price = price

def sell(price):
    global in_position

    print(f"SELL at {price}")
    logging.info(f"SELL at {price}")

    # Uncomment for real trade
    # client.order_market_sell(symbol=SYMBOL, quantity=qty)

    in_position = False

def strategy():
    global in_position, buy_price

    df = get_data()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last[4]

    # BUY CONDITION
    if prev['ema9'] < prev['ema15'] and last['ema9'] > last['ema15']:
        if not in_position:
            buy(price)

    # SELL CONDITION
    elif prev['ema9'] > prev['ema15'] and last['ema9'] < last['ema15']:
        if in_position:
            sell(price)

    # STOP LOSS
    if in_position:
        if price < buy_price * (1 - STOP_LOSS):
            print("STOP LOSS HIT")
            logging.info("STOP LOSS HIT")
            sell(price)

    print(f"Price: {price} | EMA9: {last['ema9']:.2f} | EMA15: {last['ema15']:.2f}")

# - MAIN LOOP -

print(" Bot Started...")

while True:
    try:
        strategy()
        time.sleep(20)

    except Exception as e:
        print("Error:", e)
        logging.error(f"Error: {e}")
        time.sleep(30)