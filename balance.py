from binance.client import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Connect to Binance
client = Client(API_KEY, API_SECRET)

# Get account balances
account = client.get_account()

print("===== YOUR BALANCES =====")

for asset in account['balances']:
    free = float(asset['free'])
    locked = float(asset['locked'])

    if free > 0 or locked > 0:
        print(f"{asset['asset']} | Free: {free} | Locked: {locked}")