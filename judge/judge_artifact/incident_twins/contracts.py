"""Public, JSON-only contracts. No oracle state or fixture labels."""
import hashlib
import json
from pathlib import Path

SCHEMA = "incident-twins/1"
CLAIM = {"root": "root", "resources": ["approved"], "cutoff": 50, "horizon": 100,
         "interval": "(parent_stop_confirmed, observation_horizon]"}
POLICY = "cancel-and-await-parent; request-family-cancel; delivery-races-with-worker"
CHANNELS = ("coverage", "destination", "executor", "lineage")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def read_json(path):
    return json.loads(Path(path).read_bytes())
