"""JSON-as-TEXT columns that accept lists/dicts in Python and stay compatible with existing rows."""

from __future__ import annotations

import json

from sqlalchemy.types import TEXT, TypeDecorator


class JsonList(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        if isinstance(value, str):
            return value
        return json.dumps(list(value))

    def process_result_value(self, value, dialect):
        if not value:
            return []
        if isinstance(value, list):
            return value
        try:
            data = json.loads(value)
        except (TypeError, ValueError):
            return []
        return data if isinstance(data, list) else []


class JsonDict(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "{}"
        if isinstance(value, str):
            return value
        return json.dumps(dict(value))

    def process_result_value(self, value, dialect):
        if not value:
            return {}
        if isinstance(value, dict):
            return value
        try:
            data = json.loads(value)
        except (TypeError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}
