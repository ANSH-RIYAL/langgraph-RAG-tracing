from typing import List


ALIASES = {
    "earnings": ["EarningsPerShareDiluted", "EarningsPerShareBasic", "NetIncomeLoss"],
    "eps": ["EarningsPerShareDiluted", "EarningsPerShareBasic"],
    "revenue": ["Revenues", "SalesRevenueNet"],
}


def map_alias(term: str) -> List[str]:
    t = term.lower().strip()
    return ALIASES.get(t, [term])


