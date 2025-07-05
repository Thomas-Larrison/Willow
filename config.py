import os
from dotenv import load_dotenv

load_dotenv()

KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY')
KRAKEN_API_SECRET = os.getenv('KRAKEN_API_SECRET')

WS_PUBLIC_URL = "wss://ws.kraken.com"
WS_PRIVATE_URL = "wss://ws-auth.kraken.com"
REST_API_URL = "https://api.kraken.com"
