import matplotlib.pyplot as plt
import io

def plot_price_chart(df, symbol: str):
    plt.figure(figsize=(8, 4))
    plt.plot(df["time_open"], df["quote"].apply(lambda q: q["USD"]["close"]), marker="o")
    plt.title(f"Графік ціни {symbol.upper()} за останній день")
    plt.xlabel("Час")
    plt.ylabel("Ціна (USD)")
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf