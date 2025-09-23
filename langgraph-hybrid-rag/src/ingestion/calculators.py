import pandas as pd
from typing import Optional


def pct_change(series: pd.Series, periods: int = 1) -> pd.Series:
    return series.pct_change(periods=periods)


def rolling_mean(series: pd.Series, window: int = 4) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


def filter_date_range(df: pd.DataFrame, date_col: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    if start:
        out = out[out[date_col] >= pd.to_datetime(start)]
    if end:
        out = out[out[date_col] <= pd.to_datetime(end)]
    return out




