#storage.py 

# storage.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "consos.json"


def _ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_consos() -> List[Dict[str, Any]]:
    """Charge la liste de consommations depuis le JSON."""
    _ensure_data_file()
    raw = DATA_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        # Si le fichier est corrompu, on repart de zéro (simple & safe)
        return []


def save_consos(consos: List[Dict[str, Any]]) -> None:
    """Sauvegarde la liste de consommations dans le JSON."""
    _ensure_data_file()
    DATA_FILE.write_text(json.dumps(consos, ensure_ascii=False, indent=2), encoding="utf-8")
