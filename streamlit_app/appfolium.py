import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Necesitas geopandas para parsear la respuesta y armar la capa coroplética
import geopandas as gpd
import pandas as pd

def main():
    st.title("Dashboard GIS con Microservicios")

    # 1. Seleccionar dataset
    dataset_choice = st.sidebar.selectbox(
        "Elige el dataset:",
        options=["construccion", "poblacion", "empleo"]
    )

    # 2. Desplegable para año
    year_options = ["2023", "2022", "2021"]  # Hardcode, o lo que tengas
    selected_year = st.sidebar.selectbox("Año a visualizar:", options=year_options)

    st.write(f"Has seleccionado: {dataset_choice} - Año: {selected_year}")

    # 3. Llamar a la API del microservicio
    base_url = "http://localhost:8000"
    endpoint = f"/data/{dataset_choice}?year={selected_year}"
    with st.spinner("Consultando microservicio de datos..."):
        try:
            resp = requests.get(base_url + endpoint, timeout=10)
            resp.raise_for_status()
            geojson_data = resp.json()
        except Exception as e:
            st.error(f"Error al llamar al servicio de datos: {e}")
            st.stop()

    # 4. Parsear el geojson en un GeoDataFrame para usar el Choropleth con columns=...
    try:
        gdf_remote = gpd.GeoDataFrame.from_features(geojson_data["features"])
    except Exception as e:
        st.error(f"No se pudo parsear la respuesta en GeoDataFrame: {e}")
        st.stop()

    # 5. Crear mapa Folium
    m = folium.Map(location=[43.0, -2.75], zoom_start=8, tiles="cartodbpositron")

    # 6. Choropleth con shading según la columna del año
    #    Asegúrate de que 'id_region' y 'selected_year' existan en gdf_remote
    folium.Choropleth(
        geo_data=gdf_remote.__geo_interface__,
        data=gdf_remote,
        columns=["id_region", selected_year],
        key_on="feature.properties.id_region",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"{dataset_choice} {selected_year}",
        nan_fill_color="white",
        nan_fill_opacity=0.4,
        highlight=True
    ).add_to(m)

    # 7. Añadir GeoJson con tooltip (sin rellenar color que pise el coroplético)
    folium.GeoJson(
        gdf_remote.__geo_interface__,
        name="Comarcas",
        tooltip=folium.GeoJsonTooltip(
            fields=["COMARCA", selected_year],
            aliases=["Comarca", f"{dataset_choice} {selected_year}"],
        ),
        style_function=lambda x: {
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.0  # dejar la capa base visible
        },
        highlight_function=lambda x: {
            "weight": 2,
            "color": "blue"
        }
    ).add_to(m)

    # 8. Mostrar el mapa
    st_folium(m, width=800, height=600)


if __name__ == "__main__":
    main()
