# data_service/main.py

from fastapi import FastAPI, HTTPException
import geopandas as gpd
import pandas as pd
from typing import Optional

app = FastAPI(title="Data Service for GIS")

# 1. Cargamos shapefile en memoria (en un proyecto real, podrías optimizar con caché)
try:
    gdf_comarcas = gpd.read_file("../data/COMARCAS_5000_ETRS89.shp")
    # Ajusta la columna a str y zfill si usas ID de 5 dígitos, etc.
    gdf_comarcas["id_region"] = gdf_comarcas["id_region"].astype(str).str.zfill(5)
except Exception as e:
    raise RuntimeError(f"Error al cargar el shapefile: {e}")

# Función auxiliar para leer CSV y hacer merge con shapefile
def load_and_merge(csv_path: str, year: Optional[str] = None) -> gpd.GeoDataFrame:
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except Exception as e:
        raise RuntimeError(f"Error al leer el CSV {csv_path}: {e}")

    df = df.rename(columns={"Codigo comarca": "id_region"})
    df["id_region"] = df["id_region"].astype(str).str.zfill(5)

    gdf_merged = gdf_comarcas.merge(df, on="id_region", how="left")

    # Reproyectamos a WGS84 si hace falta
    if gdf_merged.crs and gdf_merged.crs.to_string() != "EPSG:4326":
        gdf_merged = gdf_merged.to_crs(epsg=4326)

    if year:
        # Convertir la columna del año a float por si tiene comas
        gdf_merged[year] = (
            gdf_merged[year].astype(str)
            .str.replace(",", ".")
        )
        gdf_merged[year] = pd.to_numeric(gdf_merged[year], errors="coerce")

    return gdf_merged

@app.get("/")
def root():
    return {"message": "Microservicio de datos GIS activo"}

@app.get("/data/construccion")
def get_construccion(year: Optional[str] = None):
    """
    Ejemplo de endpoint para 'construccion.csv'.
    Llama: GET /data/construccion?year=2023
    """
    csv_path = "../data/construccion.csv"
    try:
        gdf_merged = load_and_merge(csv_path, year=year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return gdf_merged.__geo_interface__  # Devolvemos en formato geojson

# Podrías añadir más endpoints, p.ej.:
#/*
@app.get("/data/poblacion")
def get_poblacion(year: Optional[str] = None):
    ...
@app.get("/data/empleo")
def get_empleo(year: Optional[str] = None):
    ...
#*/
