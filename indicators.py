import pandas as pd
import pandas_ta as ta
from models import PriceData, IndicatorScore
from db import SessionLocal

class Indicators:
    def __init__(self):
        self.session = SessionLocal()

    def save_price(self, pair, price, volume):
        price_data = PriceData(pair=pair, price=price, volume=volume)
        self.session.add(price_data)
        self.session.commit()

    def get_historical_data(self, pair, interval='5min', min_candles=50):
        data = self.session.query(PriceData)\
            .filter(PriceData.pair == pair)\
            .order_by(PriceData.timestamp.asc())\
            .all()

        if not data or len(data) < min_candles:
            print(f"{pair}: not enough raw data points ({len(data)}) clearly.")
            return None

        df = pd.DataFrame([(d.timestamp, d.price, d.volume) for d in data],
                          columns=['timestamp', 'price', 'volume'])

        df.set_index(pd.to_datetime(df['timestamp']), inplace=True)
        df.drop(columns='timestamp', inplace=True)

        candles = df['price'].resample(interval).ohlc()
        candles['volume'] = df['volume'].resample(interval).sum()
        candles.dropna(inplace=True)

        if len(candles) < min_candles:
            print(f"{pair}: insufficient candles after aggregation ({len(candles)}) explicitly.")
            return None

        return candles

    def compute_indicators(self, candles):
        candles['EMA_9'] = ta.ema(candles['close'], 9)
        candles['EMA_21'] = ta.ema(candles['close'], 21)
        candles['RSI'] = ta.rsi(candles['close'], 14)

        macd = ta.macd(candles['close'])
        if macd.isna().any().any():
            print("MACD calculation NaNs explicitly detected.")
            return None

        candles = candles.join(macd)

        candles['OBV'] = ta.obv(candles['close'], candles['volume'])

        latest = candles.iloc[-1]
        if latest.isna().any():
            print("NaNs in latest candle explicitly detected.")
            return None

        indicators = latest.to_dict()
        indicators['price'] = latest['close']

        return indicators

    def compute_score(self, indicators):
        score = 0
        if indicators['EMA_9'] > indicators['EMA_21']:
            score += 20
        if indicators['MACD_12_26_9'] > indicators['MACDs_12_26_9']:
            score += 20
        if 30 < indicators['RSI'] < 70:
            score += 20
        if indicators['close'] < indicators['EMA_9'] * 0.995:
            score += 20
        if indicators['OBV'] > 0:
            score += 20
        return score

    def save_indicator_score(self, pair, score, price):
        indicator_entry = IndicatorScore(pair=pair, score=score, price=price)
        self.session.add(indicator_entry)
        self.session.commit()
