from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")


class ServiceInfo(BaseModel):
    name: Literal["Galene"] = "Galene"
    stage: Literal["foundation"] = "foundation"


@router.get("/info")
def service_info() -> ServiceInfo:
    """Public, non-personal service metadata; no inventory endpoints exist yet."""
    return ServiceInfo()
