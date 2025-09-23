import os
import matplotlib.pyplot as plt
import pandas as pd


def save_timeseries_plot(df: pd.DataFrame, x: str, y: str, out_dir: str, name: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    fig_path = os.path.join(out_dir, f"{name}.png")
    plt.figure(figsize=(8, 3))
    plt.plot(pd.to_datetime(df[x], errors="coerce"), df[y])
    plt.title(f"{y} over time")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()
    return fig_path




