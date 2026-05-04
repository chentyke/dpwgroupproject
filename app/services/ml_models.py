import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

def get_player_clusters(df: pd.DataFrame, k: int) -> dict:
    """
    Perform K-Means clustering and PCA dimensionality reduction based on the k value passed in from the front end, and return a data dictionary for front-end visualization.
    
    Parameters:
    df: pd.DataFrame, the complete dataset loaded from players_tidy.parquet
    k: int, the number of clusters specified by the frontend

    Returns:
    dict，Including player scatter data ('players') and cluster feature profiles ('cluster_profiles')
    """
    # 1. Data Filtering: Retain only players from the latest season and exclude goalkeepers
    df_ml = df[(df['season'] == 22) & (df['main_position'] != 'GK')].copy()
    
    if df_ml.empty:
        return {"players": [], "cluster_profiles": []}

    # 2. Feature Extraction
    features = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
    X_raw = df_ml[features]

    # 3. Feature Standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 4. Dynamic K-Means Clustering
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    # 5. PCA dimensionality reduction to 2 dimensions (for generating frontend scatter plot coordinates)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    # 6. Calculate the feature profile of each cluster (obtain the true capability mean via inverse standardization)
    cluster_centers_original = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_profiles = []
    
    for i in range(k):
        profile = {"cluster_id": int(i)}
        # Write the average value of each ability into a dictionary, retaining 1 decimal place.
        for j, feat in enumerate(features):
            profile[feat] = round(float(cluster_centers_original[i][j]), 1)
        cluster_profiles.append(profile)

    # 7. Assemble player-level data (for the front-end to draw scatter plots and display hover tooltips)
    result_df = df_ml[['sofifa_id', 'short_name', 'main_position', 'overall', 'value_eur']].copy()
    result_df['cluster_id'] = int(0) # 初始化格式
    result_df['cluster_id'] = cluster_labels
    
    result_df['pca_x'] = np.round(X_pca[:, 0], 3)
    result_df['pca_y'] = np.round(X_pca[:, 1], 3)

    players_data = result_df.to_dict(orient='records')

    return {
        "players": players_data,
        "cluster_profiles": cluster_profiles
    }