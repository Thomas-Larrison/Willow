import asyncio
import websockets
import json
from kraken_client import KrakenClient
from indicators import Indicators
from order_manager import OrderManager

class TradeExecutor:
    def __init__(self, pairs, threshold=70):
        self.client = KrakenClient()
        self.indicators = Indicators()
        self.order_manager = OrderManager(self.client)
        self.pairs = pairs
        self.threshold = threshold

    async def stream_data(self):
        while True:
            try:
                async with websockets.connect(self.client.WS_PUBLIC_URL, ping_interval=20, ping_timeout=20) as ws:
                    subscribe_msg = {
                        "event": "subscribe",
                        "pair": self.pairs,
                        "subscription": {"name": "ticker"}
                    }
                    await ws.send(json.dumps(subscribe_msg))
                    print(f"Subscribed explicitly to {len(self.pairs)} pairs clearly.")

                    async for message in ws:
                        data = json.loads(message)
                        if isinstance(data, list) and 'ticker' in data:
                            pair = data[-1]
                            price = float(data[1]['c'][0])
                            volume = float(data[1]['v'][1])
                            print(f"Received clearly: {pair}, Price: {price}, Volume: {volume}")
                            self.indicators.save_price(pair, price, volume)

            except websockets.exceptions.ConnectionClosedError as e:
                print(f"WebSocket explicitly closed: {e}. Clearly reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected explicit error: {e}. Clearly reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    async def evaluate_trades(self):
        while True:
            for pair in self.pairs:
                candles = self.indicators.get_historical_data(pair)
                if candles is not None:
                    indicators = self.indicators.compute_indicators(candles)
                    if indicators:
                        score = self.indicators.compute_score(indicators)
                        print(f"{pair} score explicitly computed: {score:.2f}, price: {indicators['price']}")
                        self.indicators.save_indicator_score(pair, score, indicators['price'])

                        if score >= self.threshold:
                            volume = 20 / indicators['price']
                            response = self.order_manager.place_limit_order(pair, 'buy', volume, indicators['price'])
                            print(f"Placed order explicitly: {response}")
            await asyncio.sleep(300)  # Evaluate every 5 minutes explicitly

    async def run(self):
        await asyncio.gather(
            self.stream_data(),
            self.evaluate_trades()
        )

if __name__ == "__main__":
    pairs = KrakenClient().get_top_pairs(150)
    executor = TradeExecutor(pairs)
    asyncio.run(executor.run())


