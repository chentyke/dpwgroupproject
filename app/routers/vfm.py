from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse
from app.schemas.vfm import VfmResponse
from app.services.data_repository import get_player_repository
from app.services.memory import trim_process_memory
from app.services.vfm import build_vfm_response

router = APIRouter()


@router.get("", response_model=ApiResponse[VfmResponse])
def get_vfm(
    position: str = Query(default="CAM", min_length=2, max_length=5),
    max_value: int = Query(default=120_000_000, ge=100_000),
) -> ApiResponse[VfmResponse]:
    repository = get_player_repository()
    response = build_vfm_response(
        repository,
        position=position,
        max_value=max_value,
    )
    trim_process_memory()
    return ApiResponse(data=response)
