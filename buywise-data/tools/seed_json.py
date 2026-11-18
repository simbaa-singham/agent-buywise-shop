"""Shared by the seed generators: where seed JSON goes and how it is written (ADR-046)."""
import json
from pathlib import Path

SEED_DATA = Path(__file__).resolve().parents[2] / "buywise-db" / "services" / "03-data"


def dump_lines(rows):
    """JSON array with one record per line: compact, and git diffs show exactly which record changed."""
    return "[\n" + ",\n".join(json.dumps(r, separators=(",", ":")) for r in rows) + "\n]\n"
