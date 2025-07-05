from kraken_client import KrakenClient
import time

class OrderManager:
    def __init__(self, client):
        self.client = client

    def place_limit_order(self, pair, side, volume, price):
        response = self.client.place_order(pair, side, volume, 'limit', price)
        if response['error']:
            print(f"Order placement error: {response['error']}")
            return None
        return response

    def place_market_order(self, pair, side, volume):
        response = self.client.place_order(pair, side, volume, 'market')
        if response['error']:
            print(f"Market order error: {response['error']}")
            return None
        return response

    def check_order_status(self, txid):
        urlpath = '/0/private/QueryOrders'
        nonce = int(time.time() * 1000)
        data = {'nonce': nonce, 'txid': txid}

        headers = {
            'API-Key': self.client.api_key,
            'API-Sign': self.client._sign(urlpath, data)
        }

        response = self.client.session.post(self.client.REST_API_URL + urlpath, headers=headers, data=data)
        result = response.json()

        if result['error']:
            print(f"Order status error: {result['error']}")
            return None

        return result['result'][txid]['status']
