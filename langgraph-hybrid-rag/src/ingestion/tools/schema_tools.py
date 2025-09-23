from typing import Dict, List
import pandas as pd


def get_columns(df: pd.DataFrame) -> List[str]:
    return [str(c) for c in df.columns]


def get_dtypes(df: pd.DataFrame) -> Dict[str, str]:
    return {str(c): str(t) for c, t in df.dtypes.items()}


def profile_missing(df: pd.DataFrame) -> Dict[str, int]:
    return {str(c): int(df[c].isna().sum()) for c in df.columns}


def summarize_basic_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    stats: Dict[str, Dict[str, float]] = {}
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            s = df[c].dropna()
            if s.empty:
                continue
            stats[str(c)] = {
                "count": float(s.count()),
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": float(s.mean()),
                "std": float(s.std() if s.count() > 1 else 0.0),
                "median": float(s.median()),
            }
    return stats




