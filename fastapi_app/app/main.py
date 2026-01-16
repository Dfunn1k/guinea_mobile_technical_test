import logging
from datetime import datetime
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from .core.config import get_settings
from .core.logging import configure_logging
from .db import get_session, init_db
from .models import PartnerCreate, PartnerRead, PartnerUpdate
from .services.crud import (
    get_partner_by_external_id,
    update_partner,
    upsert_partner,
)
from .services.odoo_rpc import sync_partners_to_odoo
from .services.reconciliation import ConflictError

settings = get_settings()
configure_logging(settings.log_level)
_logger = logging.getLogger(__name__)

app = FastAPI(title="External Partner API", version="1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


def get_db() -> Session:
    with get_session() as session:
        yield session


def verify_token(authorization: str = Header(default="")) -> None:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    if token != settings.api_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


@app.post("/partners", response_model=PartnerRead, dependencies=[Depends(verify_token)])
def create_partner_endpoint(payload: PartnerCreate, session: Session = Depends(get_db)):
    partner = upsert_partner(session, payload)
    return partner


@app.get("/partners/{external_id}", response_model=PartnerRead, dependencies=[Depends(verify_token)])
def get_partner_endpoint(external_id: str, session: Session = Depends(get_db)):
    partner = get_partner_by_external_id(session, external_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return partner


@app.put("/partners/{external_id}", response_model=PartnerRead, dependencies=[Depends(verify_token)])
def update_partner_endpoint(
    external_id: str,
    payload: PartnerUpdate,
    session: Session = Depends(get_db),
):
    partner = get_partner_by_external_id(session, external_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    updated = update_partner(session, partner, payload)
    return updated


@app.delete("/partners/{external_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_token)])
def delete_partner_endpoint(external_id: str, session: Session = Depends(get_db)):
    partner = get_partner_by_external_id(session, external_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    session.delete(partner)
    session.commit()


@app.post("/rpc")
async def json_rpc(request: Request, session: Session = Depends(get_db)):
    payload = await request.json()
    method = payload.get("method")
    params = payload.get("params", {})
    request_id = payload.get("id")

    try:
        verify_token(request.headers.get("Authorization", ""))
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"jsonrpc": "2.0", "error": {"code": exc.status_code, "message": exc.detail}, "id": request_id},
        )

    if method != "partner.sync":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"jsonrpc": "2.0", "error": {"code": 400, "message": "Unknown method"}, "id": request_id},
        )

    try:
        _logger.info("rpc_sync_start external_id=%s", params.get("external_id"))
        partner = upsert_partner(session, PartnerCreate(**params))
    except ConflictError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"jsonrpc": "2.0", "error": {"code": 409, "message": str(exc)}, "id": request_id},
        )
    except Exception as exc:  # pragma: no cover - safety net
        _logger.exception("RPC sync failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"jsonrpc": "2.0", "error": {"code": 500, "message": str(exc)}, "id": request_id},
        )

    return {
        "jsonrpc": "2.0",
        "result": PartnerRead.from_orm(partner).dict(),
        "id": request_id,
    }


@app.post("/sync/odoo", dependencies=[Depends(verify_token)])
def sync_partners_to_odoo_endpoint(session: Session = Depends(get_db)):
    try:
        result = sync_partners_to_odoo(session)
    except Exception as exc:
        _logger.exception("Bulk sync to Odoo failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return {"status": "ok", **result}


@app.exception_handler(ConflictError)
def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )
