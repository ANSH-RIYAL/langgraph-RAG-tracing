import pandas as pd
from .calculators import pct_change


def qoq_growth(series: pd.Series) -> pd.Series:
    return pct_change(series, periods=1)


def yoy_growth(series: pd.Series) -> pd.Series:
    return pct_change(series, periods=4)




