import pandas as pd
from binance.client import Client

client = Client()

# Fetch BTC data
klines = client.get_klines(symbol="BTCUSDT", interval="1h", limit=500)

df = pd.DataFrame(klines, columns=[
    'time','open','high','low','close','volume',
    'close_time','qav','trades','taker_base','taker_quote','ignore'
])

df['close'] = df['close'].astype(float)

# EMA Strategy
df['ema9'] = df['close'].ewm(span=9).mean()
df['ema15'] = df['close'].ewm(span=15).mean()

balance = 1000
position = 0

for i in range(1, len(df)):
    if df['ema9'][i] > df['ema15'][i] and position == 0:
        position = balance / df['close'][i]
        balance = 0

    elif df['ema9'][i] < df['ema15'][i] and position > 0:
        balance = position * df['close'][i]
        position = 0

print("Final Balance:", balance)