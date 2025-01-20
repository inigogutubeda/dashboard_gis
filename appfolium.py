import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# ========== 1. Funciones para cargar datos con caché de Streamlit ==========

@st.cache_data
def load_shapefile(shp_path: str) -> gpd.GeoDataFrame:
    """
    Carga un shapefile y devuelve un GeoDataFrame.
    """
    gdf = gpd.read_file(shp_path)
    return gdf

@st.cache_data
def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Carga un CSV con separador ; y encoding UTF-8.
    """
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    return df

def main():
    st.title("Mapa Interactivo: Unir CSV con SHP y Pintar Datos")

    # ========== 2. Leer shapefile con caché ==========

    try:
        gdf = load_shapefile("data/COMARCAS_5000_ETRS89.shp")
    except Exception as e:
        st.error(f"Error al leer el shapefile: {e}")
        st.stop()  # Detener la ejecución si no se pudo cargar

    # ========== 3. Seleccionar CSV en la barra lateral ==========

    csv_files = {
        "Construcción": "data/construccion.csv",
        "Población": "data/poblacion.csv",
        "Empleo": "data/empleo.csv"
    }
    csv_choice = st.sidebar.selectbox(
        "Elige el conjunto de datos a visualizar:",
        options=list(csv_files.keys())
    )
    chosen_csv = csv_files[csv_choice]
    
    st.write(f"Has seleccionado: **{csv_choice}**")

    # ========== 4. Leer el CSV elegido (cacheado) ==========

    try:
        df = load_csv(chosen_csv)
    except Exception as e:
        st.error(f"Error al leer {chosen_csv}: {e}")
        st.stop()

    # Suponiendo que en tu CSV la columna de unión se llama "Codigo comarca".
    # Ajusta si es distinto.
    df = df.rename(columns={"Codigo comarca": "id_region"})

    # ========== 5. Convertir "id_region" a string en ambos dataframes ==========

    gdf["id_region"] = gdf["id_region"].astype(str)
    df["id_region"] = df["id_region"].astype(str)

    # ========== 6. Merge de GDF con DF ==========

    gdf_merged = gdf.merge(df, on="id_region", how="left")

    # ========== 7. (Opcional) Reproyectar a WGS84 si fuese necesario ==========

    if gdf_merged.crs != "EPSG:4326":
        gdf_merged = gdf_merged.to_crs(epsg=4326)

    # ========== 8. Detectar columnas de tipo "año" y selector de año ==========

    # Buscamos columnas que sean puramente dígitos, por ejemplo "2023", "2022", "2019", etc.
    all_columns = gdf_merged.columns
    year_columns = [col for col in all_columns if col.isdigit()]

    if not year_columns:
        st.warning("No se han detectado columnas de años en el CSV.")
        st.stop()

    selected_year = st.sidebar.selectbox(
        "Selecciona el año a visualizar:",
        options=year_columns
    )
    st.write(f"Año seleccionado: **{selected_year}**")

    # ========== 9. Conversión de columna de datos a numérico ==========

    # Si en tu CSV los valores pueden venir con comas decimales, lo manejamos:
    gdf_merged[selected_year] = (
        gdf_merged[selected_year]
        .astype(str)
        .str.replace(",", ".")  # Convertir comas a puntos
    )
    gdf_merged[selected_year] = pd.to_numeric(gdf_merged[selected_year], errors="coerce")

    # ========== 10. Crear mapa Folium centrado en bounding box ==========

    bounds = gdf_merged.total_bounds  # [minX, minY, maxX, maxY]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="cartodbpositron")

    # ========== 11. Añadir capa coroplética (Choropleth) ==========

    # Usamos la columna "id_region" para la clave y la columna "selected_year" para los datos
    folium.Choropleth(
        geo_data=gdf_merged.__geo_interface__,
        data=gdf_merged,
        columns=["id_region", selected_year],
        key_on="feature.properties.id_region",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=(
            f"{csv_choice} - {selected_year}"
            "Haga zoom y clic en las comarcas para ver detalles."
        ),
        highlight=False
    ).add_to(m)

    # ========== 12. Añadir GeoJson con tooltip para mostrar datos ==========

    folium.GeoJson(
        gdf_merged.__geo_interface__,
        name="Comarcas",
        tooltip=folium.GeoJsonTooltip(
            # Ajusta "COMARCA" según tu shapefile
            fields=["COMARCA", selected_year],
            aliases=["Comarca", f"{csv_choice} {selected_year}"],
            localize=True
        ),
        style_function=lambda x: {
            "fillColor": "gray",
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.1
        },
        highlight_function=lambda x: {
            "weight": 2,
            "color": "blue"
        }
    ).add_to(m)

    # ========== 13. Desplegar el mapa en Streamlit ==========

    st_folium(m, width=900, height=650)


if __name__ == "__main__":
    main()
