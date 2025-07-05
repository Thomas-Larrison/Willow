from pycoingecko import CoinGeckoAPI
import requests


def get_kraken_pairs():
    response = requests.get('https://api.kraken.com/0/public/AssetPairs')
    result = response.json()['result']
    pairs = set()
    for item in result.values():
        wsname = item.get('wsname')
        if wsname:
            pairs.add(wsname)
    return pairs


def get_top_coins(limit=150):
    cg = CoinGeckoAPI()
    coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=limit)
    return [coin['symbol'].upper() for coin in coins]


def get_top_kraken_pairs(limit=150):
    kraken_pairs = get_kraken_pairs()
    top_coins = get_top_coins(limit)

    coin_mapping = {
        'BTC': ['BTC', 'XBT'],
        'DOGE': ['DOGE', 'XDG'],
        # Add other known mappings if discovered
    }

    base_currencies = ['USD', 'USDT', 'EUR', 'BTC']

    matched_pairs = set()
    for coin in top_coins:
        possible_symbols = coin_mapping.get(coin, [coin])
        for symbol in possible_symbols:
            for base in base_currencies:
                pair = f"{symbol}/{base}"
                if pair in kraken_pairs:
                    matched_pairs.add(pair)

    return list(matched_pairs)


if __name__ == "__main__":
    pairs = get_top_kraken_pairs()
    print(pairs)
