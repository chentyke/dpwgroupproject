from fastapi import APIRouter, HTTPException

from app.schemas.advanced import (
    ClusterRequest,
    ClusterResponse,
    PredictRequest,
    PredictionResponse,
)
from app.schemas.common import ApiResponse
from app.services.advanced import build_cluster_response, build_prediction_response
from app.services.data_repository import get_player_repository

router = APIRouter()


@router.post("/cluster", response_model=ApiResponse[ClusterResponse])
def post_cluster(payload: ClusterRequest) -> ApiResponse[ClusterResponse]:
    repository = get_player_repository()
    return ApiResponse(data=build_cluster_response(repository, k=payload.k))


@router.post("/predict", response_model=ApiResponse[PredictionResponse])
def post_predict(payload: PredictRequest) -> ApiResponse[PredictionResponse]:
    repository = get_player_repository()
    try:
        prediction = build_prediction_response(
            repository,
            overall=payload.overall,
            potential=payload.potential,
            age=payload.age,
            wage_eur=payload.wage_eur,
            pace=payload.pace,
            shooting=payload.shooting,
            dribbling=payload.dribbling,
            passing=payload.passing,
            defending=payload.defending,
            physic=payload.physic,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ApiResponse(data=prediction)
