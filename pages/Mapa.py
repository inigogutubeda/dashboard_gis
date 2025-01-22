import streamlit as st
import plotly.express as px
import json

# Importamos nuestras utilidades
from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import (
    prepare_geodata,
    detect_year_columns,
    convert_year_to_numeric
)

def main():
    st.title("Mapa Interactivo (Plotly): Unir CSV con SHP y Pintar Datos")

    # 1. Cargar shapefile
    try:
        gdf = load_shapefile("data/COMARCAS_5000_ETRS89.shp")
    except Exception as e:
        st.error(f"Error al leer el shapefile: {e}")
        st.stop()

    # 2. Seleccionar CSV
    csv_files = {
        "Construcción": "data/construccion.csv",
        "Contratos Indefinidos": "data/Contratos indefinidos registrados en el ano (% total contratos).csv"
    }
    csv_choice = st.sidebar.selectbox(
        "Elige el conjunto de datos a visualizar:",
        options=list(csv_files.keys())
    )
    st.write(f"Has seleccionado: **{csv_choice}**")

    chosen_csv = csv_files[csv_choice]

    # 3. Leer el CSV
    try:
        df = load_csv(chosen_csv)
    except Exception as e:
        st.error(f"Error al leer {chosen_csv}: {e}")
        st.stop()

    # 4. Preparar los datos (merge, re-proyección, etc.)
    gdf_merged = prepare_geodata(gdf, df)

    # 5. Detectar columnas de tipo año
    year_columns = detect_year_columns(gdf_merged)
    if not year_columns:
        st.warning("No se han detectado columnas de años en el CSV.")
        st.stop()

    selected_year = st.sidebar.selectbox(
        "Selecciona el año a visualizar:",
        options=year_columns
    )
    st.write(f"Año seleccionado: **{selected_year}**")

    # 6. Convertir la columna de año a numérica
    gdf_merged = convert_year_to_numeric(gdf_merged, selected_year)

    # 7. Calcular centro del mapa a partir del bounding box (para zoom/mapa)
    bounds = gdf_merged.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # 8. Convertir GeoDataFrame a GeoJSON
    #    (Plotly necesita un objeto GeoJSON; lo cargamos en un dict con `json.loads`)
    geojson_data = json.loads(gdf_merged.to_json())

    # 9. Crear el Choropleth con Plotly
    fig = px.choropleth_mapbox(
        data_frame=gdf_merged,
        geojson=geojson_data,
        locations="id_region",             # Columna que vincula con la geometría
        featureidkey="properties.id_region",  # Ruta en el GeoJSON donde está el ID
        color=selected_year,
        hover_name="COMARCA",              # Qué mostrar como título en hover
        hover_data={selected_year: True},  # Podemos mostrar la columna de año en hover
        color_continuous_scale="YlGnBu",
        mapbox_style="carto-positron",
        zoom=7.5,  # Nivel de zoom inicial
        center={"lat": center_lat, "lon": center_lon},
        opacity=0.7,
    )

    # Opcional: Ajustar layout (márgenes y colorbar)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(
            title=f"{csv_choice} - {selected_year}"
        )
    )

    # 10. Mostrar figura en Streamlit
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
