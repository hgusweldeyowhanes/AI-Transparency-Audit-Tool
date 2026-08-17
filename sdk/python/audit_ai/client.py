from __future__ import annotations

import os
import time
import uuid

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
            self.fields["completion"] = "ERROR: {}: {}".format(type(exc).__name__, exc)
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

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _headers(self):
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def log_event(self, model, prompt, **fields):
        body = {key: value for key, value in fields.items() if value is not None}
        body["model"] = model
        body["prompt"] = prompt
        body.setdefault("tags", [])
        body.setdefault("metadata", {})
        response = self._http.post(self.base_url + "/v1/events", json=body, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def log_batch(self, events):
        response = self._http.post(
            self.base_url + "/v1/events/batch",
            json={"events": events},
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

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
        response = self._http.get(self.base_url + "/v1/events", params=params, headers=self._headers())
        response.raise_for_status()
        return response.json()
