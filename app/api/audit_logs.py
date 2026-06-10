from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.domain.models.audit_log import AuditLog
from app.infrastructure.db.session import get_db
from app.schema.audit_log_schema import AuditLogResponse

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit-logs"],
)


@router.get("/", response_model=list[AuditLogResponse])
async def get_audit_logs(
    method: str | None = Query(default=None),
    status_code: int | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog)

    if method:
        query = query.where(AuditLog.method == method.upper())

    if status_code:
        query = query.where(AuditLog.status_code == status_code)

    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    return result.scalars().all()
