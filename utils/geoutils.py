# utils/geoutils.py

import geopandas as gpd
import pandas as pd

def prepare_geodata(gdf: gpd.GeoDataFrame, df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Realiza todos los pasos necesarios para preparar el GDF final:
    - Renombrar columna 'Codigo comarca' -> 'id_region' en el CSV
    - Ajustar formato de 'id_region' a 5 dígitos (zfill(5))
    - Merge (left join)
    - Reproyectar a EPSG:4326 si es necesario
    """
    # 1. Renombrar y ajustar la columna en el CSV
    df = df.rename(columns={"Codigo comarca": "id_region"})
    df["id_region"] = df["id_region"].astype(str).str.strip().str.zfill(5)

    # 2. Ajustar id_region en el shapefile
    gdf["id_region"] = gdf["id_region"].astype(str).str.strip().str.zfill(5)

    # 3. Merge
    gdf_merged = gdf.merge(df, on="id_region", how="left")

    # 4. Reproyectar si no está en WGS84
    if gdf_merged.crs != "EPSG:4326":
        gdf_merged = gdf_merged.to_crs(epsg=4326)

    return gdf_merged

def detect_year_columns(gdf_merged: gpd.GeoDataFrame) -> list:
    """
    Devuelve la lista de columnas que son dígitos puros (posibles años).
    """
    all_columns = gdf_merged.columns
    year_cols = [col for col in all_columns if col.isdigit()]
    return year_cols

def convert_year_to_numeric(gdf_merged: gpd.GeoDataFrame, selected_year: str) -> gpd.GeoDataFrame:
    """
    Convierte la columna de año a valores numéricos (p.ej. reemplazando comas por puntos).
    """
    gdf_merged[selected_year] = (
        gdf_merged[selected_year]
        .astype(str)
        .str.replace(",", ".")
    )
    gdf_merged[selected_year] = pd.to_numeric(gdf_merged[selected_year], errors="coerce")
    return gdf_merged
