import asyncio
import base64
import hashlib
import hmac
import time
import json
import websockets
import requests
import urllib.parse
from config import KRAKEN_API_KEY, KRAKEN_API_SECRET, WS_PUBLIC_URL, WS_PRIVATE_URL, REST_API_URL


class KrakenClient:
    def __init__(self):
        self.api_key = KRAKEN_API_KEY
        self.api_secret = KRAKEN_API_SECRET.encode()
        self.WS_PUBLIC_URL = WS_PUBLIC_URL
        self.WS_PRIVATE_URL = WS_PRIVATE_URL
        self.REST_API_URL = REST_API_URL
        self.session = requests.Session()

    # REST API signature method
    def _sign(self, urlpath, data):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        sig_digest = base64.b64encode(signature.digest())
        return sig_digest.decode()

    # Get Kraken account balance (REST)
    def get_account_balance(self):
        urlpath = '/0/private/Balance'
        url = self.REST_API_URL + urlpath
        nonce = int(time.time() * 1000)
        data = {'nonce': nonce}

        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign(urlpath, data)
        }

        response = self.session.post(url, headers=headers, data=data)
        return response.json()

    # Place order via Kraken REST API
    def place_order(self, pair, side, volume, ordertype='limit', price=None):
        urlpath = '/0/private/AddOrder'
        url = self.REST_API_URL + urlpath
        nonce = int(time.time() * 1000)

        data = {
            'nonce': nonce,
            'pair': pair,
            'type': side,
            'ordertype': ordertype,
            'volume': volume
        }
        if price and ordertype == 'limit':
            data['price'] = price

        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign(urlpath, data)
        }

        response = self.session.post(url, headers=headers, data=data)
        return response.json()

    # WebSocket connection: Public (price/book data) with reconnection
    async def stream_public(self, pairs):
        while True:
            try:
                async with websockets.connect(self.WS_PUBLIC_URL, ping_interval=20, ping_timeout=20) as ws:
                    subscribe_msg = {
                        "event": "subscribe",
                        "pair": pairs,
                        "subscription": {"name": "ticker"}
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    print(f"Subscribed to {pairs} ticker feed")

                    async for message in ws:
                        data = json.loads(message)
                        if isinstance(data, list):
                            print(f"Received ticker update: {data}")

            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Public WebSocket connection closed: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected error in public stream: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    # WebSocket connection: Private (trades/orders) with reconnection
    async def stream_private(self):
        while True:
            try:
                token = self._get_ws_token()
                async with websockets.connect(self.WS_PRIVATE_URL, ping_interval=20, ping_timeout=20) as ws:
                    subscribe_msg = {
                        "event": "subscribe",
                        "subscription": {
                            "name": "ownTrades",
                            "token": token
                        }
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    print("Subscribed to private ownTrades feed")

                    async for message in ws:
                        data = json.loads(message)
                        print(f"Private data update: {data}")

            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Private WebSocket connection closed: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected error in private stream: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    # Retrieve WebSocket authentication token with robust error checking
    def _get_ws_token(self):
        urlpath = '/0/private/GetWebSocketsToken'
        nonce = int(time.time() * 1000)
        data = {'nonce': nonce}

        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign(urlpath, data)
        }

        response = self.session.post(self.REST_API_URL + urlpath, headers=headers, data=data)
        result = response.json()

        if result.get('error'):
            raise Exception(f"Kraken API error getting WS token: {result['error']}")

        token = result.get('result', {}).get('token')
        if not token:
            raise Exception(f"Failed to retrieve WebSocket token: {result}")

        return token

    # Retrieve the top trading pairs
    def get_top_pairs(self, limit=150):
        response = requests.get('https://api.kraken.com/0/public/AssetPairs')
        data = response.json()['result']

        pairs = set()
        for info in data.values():
            wsname = info.get('wsname')
            if wsname:
                pairs.add(wsname)

        from pycoingecko import CoinGeckoAPI
        cg = CoinGeckoAPI()
        coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=limit)
        top_coins = {coin['symbol'].upper() for coin in coins}

        # Handle special cases explicitly
        coin_mapping = {
            'BTC': ['BTC', 'XBT'],  # BTC on CoinGecko can be XBT on Kraken
            # add other special mappings if necessary
        }

        quote_currencies = ['USD', 'USDT', 'EUR', 'BTC']
        top_kraken_pairs = set()
        for pair in pairs:
            base, quote = pair.split('/')
            for coin in top_coins:
                possible_symbols = coin_mapping.get(coin, [coin])
                if base in possible_symbols and quote in quote_currencies:
                    top_kraken_pairs.add(pair)

        return list(top_kraken_pairs)

