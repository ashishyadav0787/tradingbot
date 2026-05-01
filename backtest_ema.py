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
fees=0.001
position = 0

for i in range(1, len(df)):
    price = df['close'][i]

    # BUY (CROSS ABOVE)
    if df['ema9'][i] > df['ema15'][i] and df['ema9'][i-1] <= df['ema15'][i-1] and position == 0:
        entry_price = price        
        position = (balance / price)*(1-fees)
        balance = 0
        print(f"🟢 BUY at {price:.2f} | Index: {i}")

    # SELL (CROSS BELOW)
    elif df['ema9'][i] < df['ema15'][i] and df['ema9'][i-1] >= df['ema15'][i-1] and position > 0:
        exit_price = price
        balance = (position * price)*(1-fees)
        position = 0
        pnl = exit_price - entry_price
        print(f"🔴 SELL at {price:.2f} | Index: {i} | PnL: {pnl:.2f}")

    # 🔥 PRINT WHEN IN POSITION
    if position > 0:
        unrealized_pnl = (price - entry_price) * position
        print(f"In Trade | Price: {price:.2f} | Unrealized PnL: {unrealized_pnl:.2f}")
        
# ✅ FINAL VALUE (IMPORTANT FIX)
final_value = balance if position == 0 else position * df['close'].iloc[-1]

# ✅ TOTAL PnL
total_pnl = sum(pnl)

print("Final Value:", final_value)
print("Total PnL:", total_pnl)