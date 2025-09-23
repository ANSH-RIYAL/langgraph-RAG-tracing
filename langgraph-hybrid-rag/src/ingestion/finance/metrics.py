import pandas as pd
from typing import Optional, Tuple, Dict, List
from ..calculators import pct_change


def qoq_growth(series: pd.Series) -> pd.Series:
    return pct_change(series, periods=1)


def yoy_growth(series: pd.Series) -> pd.Series:
    return pct_change(series, periods=4)


def extract_fy(df: pd.DataFrame, metric: str, fy: int) -> Optional[Tuple[float, str]]:
    dmf = df[(df["metric"] == metric) & (df["fy"].fillna(0).astype(float) == float(fy))]
    if dmf.empty:
        return None
    fy_row = dmf[dmf["fp"].isin(["FY", "CY"])]
    if not fy_row.empty:
        return float(fy_row.iloc[0]["val"]), str(fy_row.iloc[0].get("unit"))
    return None


def extract_quarterly(df: pd.DataFrame, metric: str, fy: int) -> Dict[str, Tuple[float, str]]:
    out: Dict[str, Tuple[float, str]] = {}
    dmf = df[(df["metric"] == metric) & (df["fy"].fillna(0).astype(float) == float(fy))]
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        qrow = dmf[dmf["fp"] == q]
        if not qrow.empty:
            out[q] = (float(qrow.iloc[0]["val"]), str(qrow.iloc[0].get("unit")))
    return out


def summarize_fy_block(entity: str, fy: int, df: pd.DataFrame, metrics: List[str]) -> List[str]:
    lines: List[str] = []
    for m in metrics:
        fy_val = extract_fy(df, m, fy)
        if fy_val is not None:
            val, unit = fy_val
            lines.append(f"{entity} {fy} {m}: {val} {unit}")
        else:
            quarters = extract_quarterly(df, m, fy)
            if quarters:
                qtxt = ", ".join([f"{q}={v} {u}" for q, (v, u) in quarters.items()])
                lines.append(f"{entity} {fy} {m}: {qtxt}")
    return lines




