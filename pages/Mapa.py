import streamlit as st
import folium
from streamlit_folium import st_folium

# Importamos nuestras utilidades
from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import (
    prepare_geodata,
    detect_year_columns,
    convert_year_to_numeric
)

def main():
    st.title("Mapa Interactivo: Unir CSV con SHP y Pintar Datos")

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

    # 7. Crear mapa Folium
    bounds = gdf_merged.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="cartodbpositron")

    # 8. Choropleth
    folium.Choropleth(
        geo_data=gdf_merged.__geo_interface__,
        data=gdf_merged,
        columns=["id_region", selected_year],
        key_on="feature.properties.id_region",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="white",
        nan_fill_opacity=0.4,
        legend_name=(f"{csv_choice} - {selected_year} (Haga zoom y clic)"),
        highlight=False
    ).add_to(m)

    # 9. Capa adicional con tooltip
    folium.GeoJson(
        gdf_merged.__geo_interface__,
        name="Comarcas",
        tooltip=folium.GeoJsonTooltip(
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

    # 10. Mostrar mapa en Streamlit
    st_folium(m, width=700, height=500)

if __name__ == "__main__":
    main()
