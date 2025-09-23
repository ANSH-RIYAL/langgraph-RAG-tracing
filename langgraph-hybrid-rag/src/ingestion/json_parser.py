from typing import Dict, Any
import json
import pandas as pd


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_companyfacts(data: Dict[str, Any]) -> pd.DataFrame:
    # SEC CompanyFacts dei units pattern: data["facts"][taxonomy][metric]["units"][unit] -> list of dicts
    rows = []
    facts = data.get("facts", {})
    for taxonomy, metrics in facts.items():
        for metric, mdata in metrics.items():
            units = mdata.get("units", {})
            for unit_name, entries in units.items():
                for e in entries:
                    rows.append({
                        "metric": metric,
                        "unit": unit_name,
                        "end": e.get("end"),
                        "val": e.get("val"),
                        "fy": e.get("fy"),
                        "fp": e.get("fp"),
                        "form": e.get("form"),
                    })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df




