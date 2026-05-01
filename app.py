from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os
from binance.client import Client
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

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

st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("🚀 Trading Dashboard")

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

# ------------------ DATA ------------------

@st.cache_data
def get_data():
    klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=300)
    df = pd.DataFrame(klines, columns=[
        'time','open','high','low','close','volume',
        'close_time','qav','trades','taker_base','taker_quote','ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema15'] = df['close'].ewm(span=15).mean()

    df['sma'] = df['close'].rolling(20).mean()
    df['std'] = df['close'].rolling(20).std()
    df['upper'] = df['sma'] + 2 * df['std']
    df['lower'] = df['sma'] - 2 * df['std']

    return df

df = get_data()

# RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['rsi'] = compute_rsi(df['close'])

# ------------------ STRATEGY SELECT ------------------

strategy = st.selectbox("Select Strategy", ["EMA + RSI", "Bollinger"])

# ------------------ BACKTEST ------------------

balance = 1000
position = 0
entry_price = 0
entry_time = None

SL = 0.02
TP = 0.03
FEE = 0.001

trades = []
buy_idx = []
sell_idx = []

TREND_MIN = 20
COOLDOWN = 10
USE_VOL_FILTER = True
VOL_MIN = df['std'].mean() * 0.5
TREND_THRESHOLD = 30
last_trade_index = -100

for i in range(20, len(df)-1):

    price = df['close'][i]
    next_price = df['close'][i+1]
    next_time = df['time'][i+1]

    trend_strength = abs(df['ema9'][i] - df['ema15'][i])

    # ---------- MARKET TYPE ----------
    if trend_strength > TREND_THRESHOLD:
        market_type = "TRENDING"
    else:
        market_type = "SIDEWAYS"

    if i - last_trade_index < COOLDOWN:
        continue

    # ---------- STRATEGY ----------
    if market_type == "TRENDING":
        cross_up = df['ema9'][i] > df['ema15'][i] and df['ema9'][i-1] <= df['ema15'][i-1]
        trend_up = df['ema9'][i] > df['ema15'][i]
        pullback = price <= df['ema9'][i] * 1.01

        buy_condition = trend_up and pullback and cross_up
        sell_condition = df['ema9'][i] < df['ema15'][i]

    else:
        buy_condition = price < df['lower'][i] and df['rsi'][i] < 30
        sell_condition = price > df['upper'][i]

    # ---------- BUY ----------
    if position == 0 and buy_condition:
        position = (balance / next_price) * (1 - FEE)
        entry_price = next_price
        entry_time = next_time
        balance = 0
        buy_idx.append(i)
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
            sell_idx.append(i)
            last_trade_index = i

st.write("Current Market Type:", market_type)
trades_df = pd.DataFrame(trades)

# ------------------ CHART ------------------

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df['time'],
    open=df['open'].astype(float),
    high=df['high'].astype(float),
    low=df['low'].astype(float),
    close=df['close'],
    name="Price"
))

fig.add_trace(go.Scatter(x=df['time'], y=df['ema9'], name="EMA 9"))
fig.add_trace(go.Scatter(x=df['time'], y=df['ema15'], name="EMA 15"))

fig.add_trace(go.Scatter(x=df['time'], y=df['upper'], name="Upper Band"))
fig.add_trace(go.Scatter(x=df['time'], y=df['lower'], name="Lower Band"))

fig.add_trace(go.Scatter(
    x=df['time'].iloc[buy_idx],
    y=df['close'].iloc[buy_idx],
    mode='markers',
    name='BUY',
    marker=dict(color='green', size=10)
))

fig.add_trace(go.Scatter(
    x=df['time'].iloc[sell_idx],
    y=df['close'].iloc[sell_idx],
    mode='markers',
    name='SELL',
    marker=dict(color='red', size=10)
))

fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ------------------ RESULTS ------------------

if not trades_df.empty:
    st.metric("Total PnL", f"{trades_df['pnl'].sum():.2f}")
    st.metric("Win Rate", f"{(trades_df['pnl'] > 0).mean()*100:.2f}%")

    st.dataframe(trades_df)

    st.line_chart(trades_df['pnl'].cumsum())
else:
    st.warning("No trades generated yet")