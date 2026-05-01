import requests
import time

while True:
    data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
    print("BTC Price:", data["price"])
    time.sleep(5)