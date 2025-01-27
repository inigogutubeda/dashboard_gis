import streamlit as st
import plotly.express as px
import json
from streamlit_plotly_events import plotly_events
from utils.metadata import load_datasets_metadata

# Importamos nuestras utilidades
from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import (
    prepare_geodata,
    detect_year_columns,
    convert_year_to_numeric
)

st.set_page_config(layout="wide")

def main():
    st.title("Mapa Interactivo de Datos por Comarca")

    # 1. Cargar shapefile
    try:
        gdf = load_shapefile("data/COMARCAS_5000_ETRS89.shp")
    except Exception as e:
        st.error(f"Error al leer el shapefile: {e}")
        st.stop()

    # 2. Seleccionar CSV
    csv_files = {
        "Porcentaje establecimeintos sector cosntruccion (% sobre total)": "data/Porcentaje establecimientos sector construccion sobre el total.csv",
        "Contratos Indefinidos": "data/Contratos indefinidos registrados en el ano (% total contratos).csv",
        "Contratos Anuales": "data/Contratos registrados en el ano ( habitantes).csv",
        "Densidad comercial minorista": "data/Densidad comercial minorista ( habitantes).csv",
        "Empleo generado microempresas": "data/Empleo generado por las microempresas (0-9 empleados) (%).csv",
        "Indice rotación contractual": "data/Indice de rotacion contractual (contratos_personas).csv",
        "Población contratada año": "data/Poblacion contratada en el ano ( habitantes).csv",
        "Mayor 16 años. Sector servicios": "data/Poblacion de 16 y mas anos ocupada en el sector servicios (%).csv"
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

    # Convertir todas las columnas de años a numérico
    for col in year_columns:
        gdf_merged = convert_year_to_numeric(gdf_merged, col)

    # Seleccionar el año a visualizar
    selected_year = st.sidebar.selectbox(
        "Selecciona el año a visualizar:",
        options=year_columns
    )
    st.write(f"Año seleccionado: **{selected_year}**")

    # Calcular centro del mapa
    bounds = gdf_merged.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # Convertir GeoDataFrame a GeoJSON
    geojson_data = json.loads(gdf_merged.to_json())

    # Crear el Choropleth con Plotly
    fig = px.choropleth_mapbox(
        data_frame=gdf_merged,
        geojson=geojson_data,
        locations="id_region",
        featureidkey="properties.id_region",
        color=selected_year,
        hover_name="COMARCA",
        hover_data={selected_year: True},
        color_continuous_scale="YlGnBu",
        mapbox_style="carto-positron",
        zoom=7.5,
        center={"lat": center_lat, "lon": center_lon},
        opacity=0.7,
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title=f"{csv_choice} - {selected_year}")
    )

    # Usar streamlit-plotly-events para capturar clics en el mapa
    selected_points = plotly_events(
        fig,
        click_event=True,  # Captura eventos de clic
        hover_event=False,  # Desactiva captura de hover
        select_event=False  # Desactiva eventos de selección
    )

    # Mostrar estadísticas si se selecciona un punto en el mapa
    if selected_points:
        selected_region_id = selected_points[0]["pointIndex"]
        selected_comarca = gdf_merged.iloc[selected_region_id]["COMARCA"]

        st.subheader(f"Estadísticas históricas para la comarca: {selected_comarca}")

        # Filtrar datos de la comarca seleccionada
        df_comarca = gdf_merged[gdf_merged["COMARCA"] == selected_comarca]

        # Calcular min, max y media para todas las columnas de años
        valor_min = df_comarca[year_columns].min().min()
        valor_max = df_comarca[year_columns].max().max()
        valor_mean = df_comarca[year_columns].mean().mean()

        st.write(f"- **Mínimo histórico**: {valor_min:.2f}")
        st.write(f"- **Máximo histórico**: {valor_max:.2f}")
        st.write(f"- **Media histórica**: {valor_mean:.2f}")


if __name__ == "__main__":
    main()
