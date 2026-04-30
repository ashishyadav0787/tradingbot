import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from binance.client import Client
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

#streamlit run dashboard_full.py
# - SETUP -
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
INTERVAL = "5m"

st.set_page_config(page_title="Quant Trading Dashboard", layout="wide")

st.title("🚀 Quant Trading Dashboard")

# AUTO REFRESH
st_autorefresh(interval=5000, key="refresh")

# - PRICE TRACKER -

st.subheader("💰 Live BTC Price")

price_data = client.get_symbol_ticker(symbol=SYMBOL)
price = float(price_data["price"])

st.metric("BTC Price", f"${price:.2f}")

# - BALANCE -

st.subheader("🏦 Account Balance")

try:
    account = client.get_account()
    balances = []

    for asset in account['balances']:
        free = float(asset['free'])
        if free > 0:
            balances.append([asset['asset'], free])

    balance_df = pd.DataFrame(balances, columns=["Asset", "Balance"])
    st.dataframe(balance_df)

except Exception as e:
    st.warning("Balance not available (API issue or permissions)")

# - MARKET DATA -

@st.cache_data
def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=200)

    df = pd.DataFrame(klines, columns=[
        'time','open','high','low','close','volume',
        'close_time','qav','trades','taker_base','taker_quote','ignore'
    ])

    df['close'] = df['close'].astype(float)
    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema15'] = df['close'].ewm(span=15).mean()

    return df

df = get_data()

# - SIGNAL -

st.subheader("📊 Trading Signal")

last = df.iloc[-1]
prev = df.iloc[-2]

if prev['ema9'] < prev['ema15'] and last['ema9'] > last['ema15']:
    st.success("🟢 BUY SIGNAL")

elif prev['ema9'] > prev['ema15'] and last['ema9'] < last['ema15']:
    st.error("🔴 SELL SIGNAL")

else:
    st.warning("⚪ NO SIGNAL")

# - CHART -

st.subheader("📈 Candlestick + EMA Chart")

# Convert time
df['time'] = pd.to_datetime(df['time'], unit='ms')

fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=df['time'],
    open=df['open'].astype(float),
    high=df['high'].astype(float),
    low=df['low'].astype(float),
    close=df['close'],
    name="Price"
))

# EMA 9
fig.add_trace(go.Scatter(
    x=df['time'],
    y=df['ema9'],
    mode='lines',
    name='EMA 9',
    line=dict(width=2)
))

# EMA 15
fig.add_trace(go.Scatter(
    x=df['time'],
    y=df['ema15'],
    mode='lines',
    name='EMA 15',
    line=dict(width=2)
))

# Layout styling
fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False,
    height=600,
    template="plotly_dark"
)
buy_signals = df[(df['ema9'] > df['ema15']) & (df['ema9'].shift(1) <= df['ema15'].shift(1))]
sell_signals = df[(df['ema9'] < df['ema15']) & (df['ema9'].shift(1) >= df['ema15'].shift(1))]

fig.add_trace(go.Scatter(
    x=buy_signals['time'],
    y=buy_signals['close'],
    mode='markers',
    name='BUY',
    marker=dict(size=10, symbol='triangle-up')
))

fig.add_trace(go.Scatter(
    x=sell_signals['time'],
    y=sell_signals['close'],
    mode='markers',
    name='SELL',
    marker=dict(size=10, symbol='triangle-down')
))
st.plotly_chart(fig, use_container_width=True)
# - BACKTEST -

st.subheader("🧪 Backtest Result")

balance = 1000
position = 0

for i in range(1, len(df)):
    if df['ema9'][i] > df['ema15'][i] and position == 0:
        position = balance / df['close'][i]
        balance = 0

    elif df['ema9'][i] < df['ema15'][i] and position > 0:
        balance = position * df['close'][i]
        position = 0

final_value = balance if position == 0 else position * df['close'].iloc[-1]

st.metric("Final Backtest Value", f"${final_value:.2f}")

# - TRADE LOG -

st.subheader("📜 Trading Log")

if os.path.exists("trading.log"):
    try:
        log_df = pd.read_csv("trading.log", names=["time", "message"])
        st.dataframe(log_df.tail(20))
    except:
        st.write("Log format issue")
else:
    st.write("No logs yet...")