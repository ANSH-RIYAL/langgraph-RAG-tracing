import os
import json
from typing import List, Dict


def write_jsonl_corpus(chunks: List[Dict], out_dir: str, filename: str = "corpus.jsonl") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
    return path




