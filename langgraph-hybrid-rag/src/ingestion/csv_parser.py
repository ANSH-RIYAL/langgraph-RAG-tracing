from typing import Dict, Any
import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def profile_csv(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": [str(c) for c in df.columns],
        "dtypes": {str(c): str(t) for c, t in df.dtypes.items()},
        "missing": {str(c): int(df[c].isna().sum()) for c in df.columns},
    }
    return profile




