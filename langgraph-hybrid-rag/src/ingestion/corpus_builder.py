import os
from typing import List, Dict
import pandas as pd
from .tools.schema_tools import get_columns, get_dtypes, profile_missing, summarize_basic_stats
from .tools.agg_tools import aggregate
from .tools.time_tools import to_datetime, resample_period
from .json_parser import flatten_companyfacts
from .finance.metrics import summarize_fy_block


def build_from_csv(path: str) -> List[Dict]:
    df = pd.read_csv(path)
    rows, cols = df.shape
    columns = get_columns(df)
    dtypes = get_dtypes(df)
    missing = profile_missing(df)
    stats = summarize_basic_stats(df)
    head = df.head(10).to_csv(index=False)
    # Time aggregations if Date present
    agg_txt = ""
    if "Date" in df.columns:
        dfa = to_datetime(df, "Date")
        monthly = resample_period(dfa.rename(columns={"Close": "Close"}), "Date", "M", {"Close": "mean"})
        agg_txt = monthly.head(12).to_csv(index=False)
    desc = (
        f"Source: {path}\n"
        f"Rows: {rows}, Cols: {cols}\n"
        f"Columns: {', '.join(columns)}\n"
        f"DTypes: {dtypes}\n"
        f"Missing: {missing}\n"
        f"BasicStats: {stats}\n"
        f"MonthlyCloseMean (if applicable):\n{agg_txt}\n"
        f"Sample (10 rows):\n{head}\n"
    )
    # Single chunk per CSV description; chunker will segment
    return [{
        "document_id": f"doc_{abs(hash(path)) % (10**8):08d}",
        "text": desc,
        "source_doc": os.path.basename(path),
        "source_path": path,
        "chunk_index": 0,
        "page_number": None,
    }]


def build_from_companyfacts(path: str, data: Dict) -> List[Dict]:
    df = flatten_companyfacts(data)
    if df.empty:
        return []
    entity = data.get("entityName", "Unknown Entity")
    cols = ", ".join([str(c) for c in df.columns])
    # 2018-2025 sweeps for key metrics to enlarge corpus
    lines: List[str] = []
    for fy in range(2018, 2026):
        lines.extend(summarize_fy_block(entity, fy, df, [
            "EarningsPerShareDiluted",
            "EarningsPerShareBasic",
            "NetIncomeLoss",
            "Revenues",
            "SalesRevenueNet",
        ]))
    head = df.head(50).to_csv(index=False)
    desc = (
        f"Source: {path}\n"
        f"Entity: {entity}\n"
        f"Columns: {cols}\n"
        f"FY Summaries (2018-2025):\n" + "\n".join(lines) + "\n"
        f"Sample (50 rows):\n{head}\n"
    )
    return [{
        "document_id": f"doc_{abs(hash(path)) % (10**8):08d}",
        "text": desc,
        "source_doc": os.path.basename(path),
        "source_path": path,
        "chunk_index": 0,
        "page_number": None,
    }]




