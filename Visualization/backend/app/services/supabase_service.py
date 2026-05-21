from typing import Any, Dict, List, Optional

import httpx

from ..config import settings


class SupabaseService:
    def __init__(self) -> None:
        self._base = settings.supabase_url.rstrip("/") if settings.supabase_url else ""
        self._key = settings.supabase_service_role_key

    @property
    def enabled(self) -> bool:
        return bool(self._base and self._key)

    def _headers(self) -> Dict[str, str]:
        return {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def save_search_run(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        row = {
            "mode": payload["mode"],
            "algorithm": payload["algorithm"],
            "found": payload.get("found", False),
            "message": payload.get("message"),
            "elapsed_ms": payload.get("elapsed_ms"),
            "steps_count": payload.get("steps_count", 0),
            "start_state": payload.get("start_state"),
            "path": payload.get("path"),
            "tree": payload.get("tree"),
        }
        url = f"{self._base}/rest/v1/search_runs"
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=row, headers=self._headers())
            if resp.status_code >= 400:
                return None
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0]
            if isinstance(data, dict):
                return data
        return None

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        url = f"{self._base}/rest/v1/search_runs"
        params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": str(min(limit, 50)),
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, params=params, headers=self._headers())
            if resp.status_code >= 400:
                return []
            return resp.json() or []


supabase_service = SupabaseService()
