from typing import Dict
import pandas as pd


def to_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.copy()
    out[col] = pd.to_datetime(out[col], errors="coerce")
    return out


def filter_date_range(df: pd.DataFrame, col: str, start: str | None, end: str | None) -> pd.DataFrame:
    out = to_datetime(df, col)
    if start:
        out = out[out[col] >= pd.to_datetime(start)]
    if end:
        out = out[out[col] <= pd.to_datetime(end)]
    return out


def resample_period(df: pd.DataFrame, date_col: str, period: str, agg_spec: Dict[str, str]) -> pd.DataFrame:
    out = to_datetime(df, date_col)
    # Normalize deprecated codes
    period = 'ME' if period == 'M' else period
    out = out.set_index(date_col).resample(period).agg(agg_spec).reset_index()
    return out


