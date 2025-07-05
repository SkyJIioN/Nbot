# services/trend_lines.py
import numpy as np

def calculate_trend_lines(close_prices, num_points=50):
    """
    Обчислює тренд, лінію підтримки і лінію опору на основі останніх `num_points` закриттів.
    """
    if len(close_prices) < num_points:
        raise ValueError("Недостатньо даних для аналізу тренду")

    data = close_prices[-num_points:]

    x = np.arange(len(data))
    y = np.array(data)

    # Підгонка лінійного тренду
    coef = np.polyfit(x, y, 1)
    trend_slope = coef[0]

    if trend_slope > 0:
        trend = "висхідний"
    elif trend_slope < 0:
        trend = "нисхідний"
    else:
        trend = "боковий"

    # Лінія підтримки — мінімум з останніх точок
    support = float(np.min(data))
    # Лінія опору — максимум
    resistance = float(np.max(data))

    return trend, support, resistance