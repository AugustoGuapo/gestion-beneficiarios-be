from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id_audit_log: int
    username: str | None
    method: str
    endpoint: str
    action: str
    status_code: int
    ip_address: str | None
    payload: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True
