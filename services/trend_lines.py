import pandas as pd
import numpy as np

def calculate_trend_info(df: pd.DataFrame, lookback: int = 50):
    df = df[-lookback:].copy()
    df.reset_index(drop=True, inplace=True)

    lows = df['low']
    highs = df['high']

    # Підтримка (support) — найнижча точка
    support = lows.min()
    # Опір (resistance) — найвища точка
    resistance = highs.max()

    # Визначення тренду
    price_diff = df['close'].iloc[-1] - df['close'].iloc[0]
    trend = "висхідний" if price_diff > 0 else "нисхідний" if price_diff < 0 else "нейтральний"

    return trend, round(support, 5), round(resistance, 5)