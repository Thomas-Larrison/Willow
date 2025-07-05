import asyncio
from kraken_client import KrakenClient

async def main():
    client = KrakenClient()

    # Test account balance retrieval
    balance = client.get_account_balance()
    print("Account Balance:", balance)

    # Start websocket streams concurrently
    await asyncio.gather(
        client.stream_public(["BTC/USD", "ETH/USD"]),
        client.stream_private()
    )


if __name__ == "__main__":
    asyncio.run(main())

