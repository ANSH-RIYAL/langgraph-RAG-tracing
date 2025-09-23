from typing import Dict, List, Tuple
import pandas as pd


def aggregate(df: pd.DataFrame, by: List[str] | None, metrics: Dict[str, List[str]]) -> pd.DataFrame:
    if by:
        return df.groupby(by).agg(metrics).reset_index()
    return df.agg(metrics)


def filter_rows(df: pd.DataFrame, conditions: List[Tuple[str, str, object]]) -> pd.DataFrame:
    out = df.copy()
    for col, op, val in conditions:
        if op == "==":
            out = out[out[col] == val]
        elif op == ">":
            out = out[out[col] > val]
        elif op == ">=":
            out = out[out[col] >= val]
        elif op == "<":
            out = out[out[col] < val]
        elif op == "<=":
            out = out[out[col] <= val]
        elif op == "!=":
            out = out[out[col] != val]
    return out


def select_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    return df[cols]


def sort_by(df: pd.DataFrame, cols: List[str], ascending: List[bool] | None = None) -> pd.DataFrame:
    ascending = ascending or [True] * len(cols)
    return df.sort_values(by=cols, ascending=ascending)




