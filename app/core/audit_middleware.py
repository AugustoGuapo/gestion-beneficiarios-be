import json
import logging

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import get_username_from_authorization_header
from app.domain.models.audit_log import AuditLog
from app.infrastructure.db.session import SessionLocal

logger = logging.getLogger(__name__)

IGNORED_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
}


def get_action_from_method(method: str) -> str:
    actions = {
        "GET": "READ",
        "POST": "CREATE",
        "PUT": "UPDATE",
        "PATCH": "UPDATE",
        "DELETE": "DELETE",
    }

    return actions.get(method, "UNKNOWN")


def mask_sensitive_payload(payload):
    if not isinstance(payload, dict):
        return payload

    sensitive_keys = {
        "password",
        "token",
        "secret",
        "access_token",
        "refresh_token",
    }

    return {
        key: "***" if key.lower() in sensitive_keys else value for key, value in payload.items()
    }


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if request.url.path in IGNORED_PATHS:
            return response

        payload = None

        try:
            if request.method in {"POST", "PUT", "PATCH"}:
                body = await request.body()

                if body:
                    payload = json.loads(body.decode("utf-8"))
                    payload = mask_sensitive_payload(payload)

        except Exception:
            payload = None

        try:
            async with SessionLocal() as db:
                audit_log = AuditLog(
                    username=get_username_from_authorization_header(
                        request.headers.get("authorization")
                    ),
                    method=request.method,
                    endpoint=request.url.path,
                    action=get_action_from_method(request.method),
                    status_code=response.status_code,
                    ip_address=request.client.host if request.client else None,
                    payload=payload,
                )

                db.add(audit_log)
                await db.commit()

        except Exception:
            logger.exception("Error guardando auditoría")

        return response
