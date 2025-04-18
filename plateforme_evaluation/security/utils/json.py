# security/utils/json.py
import json
from datetime import datetime
from uuid import UUID

class SecurityJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (frozenset, set)):
            return list(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)