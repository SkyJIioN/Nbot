import numpy as np

def detect_trend_lines(prices: list[float]):
    if len(prices) < 2:
        return None, None, "нейтральний"

    x = np.arange(len(prices))
    y = np.array(prices)

    # Лінія тренду (лінійна регресія)
    slope, intercept = np.polyfit(x, y, 1)
    trend = "висхідний" if slope > 0 else "нисхідний" if slope < 0 else "нейтральний"

    # Лінії підтримки і опору
    support = min(prices)
    resistance = max(prices)

    return round(support, 5), round(resistance, 5), trend