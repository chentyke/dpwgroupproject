from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse
from app.schemas.fairness import FairnessByLeagueResponse, NationalityHeatmapResponse
from app.services.data_repository import get_player_repository
from app.services.fairness import build_fairness_by_league, build_nationality_heatmap

router = APIRouter()


@router.get("/wages-by-league", response_model=ApiResponse[FairnessByLeagueResponse])
def get_wages_by_league(
    overall_min: int = Query(default=80, ge=1, le=99),
    overall_max: int = Query(default=90, ge=1, le=99),
) -> ApiResponse[FairnessByLeagueResponse]:
    repository = get_player_repository()
    return ApiResponse(
        data=build_fairness_by_league(
            repository,
            overall_min=overall_min,
            overall_max=overall_max,
        )
    )


@router.get("/nationality-heatmap", response_model=ApiResponse[NationalityHeatmapResponse])
def get_nationality_heatmap() -> ApiResponse[NationalityHeatmapResponse]:
    repository = get_player_repository()
    return ApiResponse(data=build_nationality_heatmap(repository))

