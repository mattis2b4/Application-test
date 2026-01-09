# storage.py
from __future__ import annotations

from typing import Any, Dict, List
import requests
import streamlit as st


def _headers() -> Dict[str, str]:
    key = st.secrets["SUPABASE_ANON_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _base_url() -> str:
    return st.secrets["SUPABASE_URL"].rstrip("/") + "/rest/v1/consos"


def load_consos() -> List[Dict[str, Any]]:
    # tri : date desc puis created_at desc
    url = _base_url()
    params = {
        "select": "*",
        "order": "date.desc,created_at.desc",
    }
    r = requests.get(url, headers=_headers(), params=params, timeout=20)
    r.raise_for_status()
    return r.json()  # liste de dicts


def add_conso(item: Dict[str, Any]) -> None:
    url = _base_url()
    r = requests.post(url, headers=_headers(), json=item, timeout=20)
    r.raise_for_status()


def delete_conso(conso_id: str) -> None:
    url = _base_url()
    params = {"id": f"eq.{conso_id}"}
    r = requests.delete(url, headers=_headers(), params=params, timeout=20)
    r.raise_for_status()
