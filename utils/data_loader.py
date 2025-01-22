# utils/data_loader.py

import streamlit as st
import geopandas as gpd
import pandas as pd

@st.cache_data
def load_shapefile(shp_path: str) -> gpd.GeoDataFrame:
    """
    Carga un Shapefile y devuelve un GeoDataFrame.
    """
    return gpd.read_file(shp_path)

@st.cache_data
def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Carga un CSV con separador ; y encoding UTF-8.
    """
    return pd.read_csv(csv_path, sep=';', encoding='utf-8')
