from fastapi import APIRouter
from app.services.ml_models import get_player_clusters
# Suppose there is a global data acquisition dependency or method get_dataframe() in the project

router = APIRouter()

@router.post("/api/cluster")
def cluster_players(k: int = 5):
    """
    K-Means Player Style Clustering Interface
    """
    df = get_dataframe()
    return get_player_clusters(df, k)