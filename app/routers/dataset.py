from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.dataset import CleaningReport, DatasetSummary
from app.services.data_repository import get_player_repository
from app.services.dataset import build_cleaning_report, build_dataset_summary

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[DatasetSummary])
def get_dataset_summary() -> ApiResponse[DatasetSummary]:
    repository = get_player_repository()
    return ApiResponse(data=build_dataset_summary(repository))


@router.get("/cleaning-report", response_model=ApiResponse[CleaningReport])
def get_cleaning_report() -> ApiResponse[CleaningReport]:
    repository = get_player_repository()
    return ApiResponse(data=build_cleaning_report(repository))

