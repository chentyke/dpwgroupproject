from fastapi import APIRouter

from app.routers import advanced, dataset, fairness, vfm


api_router = APIRouter()
api_router.include_router(dataset.router, prefix="/dataset", tags=["dataset"])
api_router.include_router(vfm.router, prefix="/vfm", tags=["value-for-money"])
api_router.include_router(fairness.router, prefix="/fairness", tags=["fairness"])
api_router.include_router(advanced.router, tags=["advanced"])

