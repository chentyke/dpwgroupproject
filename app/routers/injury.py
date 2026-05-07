from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.injury import FutureRiskResponse
from app.services.data_repository import get_player_repository
from app.services.injury import build_future_risk_response
from app.services.memory import trim_process_memory

router = APIRouter()


@router.get("/future-risk", response_model=ApiResponse[FutureRiskResponse])
def get_future_risk() -> ApiResponse[FutureRiskResponse]:
    repository = get_player_repository()
    response = build_future_risk_response(repository)
    trim_process_memory()
    return ApiResponse(data=response)
