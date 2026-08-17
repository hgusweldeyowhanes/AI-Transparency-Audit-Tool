from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, List, Optional

import httpx


class AuditSpan:
    def __init__(self, client, **kwargs):
        self._client = client
        self.fields = dict(kwargs)
        self.fields.setdefault("trace_id", str(uuid.uuid4()))
        self._t0 = None

    def __enter__(self):
        self._t0 = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._t0 is not None and "latency_ms" not in self.fields:
            self.fields["latency_ms"] = int((time.time() - self._t0) * 1000)
        if exc is not None and not self.fields.get("completion"):
            self.fields["completion"] = "ERROR: " + type(exc).__name__ + ": " + str(exc)
        if self.fields.get("prompt") is not None:
            self._client.log_event(**self.fields)
        return False

    def log(self, **kwargs):
        self.fields.update(kwargs)


class AuditClient:
    def __init__(self, api_key=None, base_url=None, timeout=15.0):
        self.api_key = api_key or os.environ.get("AUDIT_API_KEY", "audit_demo_key")
        self.base_url = (base_url or os.environ.get("AUDIT_BASE_URL") or "http://localhost:8000").rstrip("/")
        self._http = httpx.Client(timeout=timeout)

    def close(self):
        self._http.close()

    def _headers(self):
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def log_event(
        self,
        model,
        prompt,
        completion="",
        provider=None,
        system_prompt=None,
        prompt_tokens=0,
        completion_tokens=0,
        cost_usd=None,
        latency_ms=0,
        prompt_version=None,
        user_id=None,
        session_id=None,
        tags=None,
        metadata=None,
        trace_id=None,
    ):
        body = {
            "model": model,
            "prompt": prompt,
            "completion": completion,
            "provider": provider,
            "system_prompt": system_prompt,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
            "prompt_version": prompt_version,
            "user_id": user_id,
            "session_id": session_id,
            "tags": tags or [],
            "metadata": metadata or {},
            "trace_id": trace_id,
        }
        r = self._http.post(self.base_url + "/v1/events", json=body, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def log_batch(self, events):
        r = self._http.post(
            self.base_url + "/v1/events/batch",
            json={"events": events},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    def trace(self, **kwargs):
        return AuditSpan(self, **kwargs)

    def search(self, q=None, model=None, flag=None, limit=50):
        params = {"limit": limit}
        if q:
            params["q"] = q
        if model:
            params["model"] = model
        if flag:
            params["flag"] = flag
        r = self._http.get(self.base_url + "/v1/events", params=params, headers=self._headers())
        r.raise_for_status()
        return r.json()
