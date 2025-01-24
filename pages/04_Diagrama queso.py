# pages/03_pie_chart.py

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import prepare_geodata, detect_year_columns, convert_year_to_numeric

st.set_page_config(layout="wide")

def main():
    st.title("Diagrama de Queso: Distribución por Región")

    # 1. Cargar Shapefile
    try:
        gdf = load_shapefile("data/COMARCAS_5000_ETRS89.shp")
    except Exception as e:
        st.error(f"Error al leer el shapefile: {e}")
        st.stop()

    # 2. Seleccionar CSV
    csv_files = {
        "Construcción": "data/construccion.csv",
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

    # 3. Cargar CSV
    try:
        df = load_csv(chosen_csv)
    except Exception as e:
        st.error(f"Error al leer {chosen_csv}: {e}")
        st.stop()

    # 4. Merge y reproyección
    gdf_merged = prepare_geodata(gdf, df)

    # 5. Detectar columnas de tipo año
    year_columns = detect_year_columns(gdf_merged)
    if not year_columns:
        st.warning("No se han detectado columnas de años en el CSV.")
        st.stop()

    # 6. Seleccionar año
    selected_year = st.sidebar.selectbox(
        "Selecciona el año a visualizar:",
        options=year_columns
    )

    # 7. Convertir la columna de año a numérico
    gdf_merged = convert_year_to_numeric(gdf_merged, selected_year)

    st.write(f"Año seleccionado: **{selected_year}**")

    # 8. Crear un DataFrame auxiliar: [COMARCA, Valor]
    df_pie = gdf_merged[["COMARCA", selected_year]].copy()
    df_pie.columns = ["COMARCA", "Valor"]  # Renombramos para claridad

    # Opcional: eliminar filas con NaN
    df_pie.dropna(subset=["Valor"], inplace=True)

    # 9. Construir el pie chart con Plotly
    fig = px.pie(
        df_pie,
        names="COMARCA",
        values="Valor",
        title=f"Distribución de {csv_choice} en {selected_year}",
        hole=0.0  # 0 para un pie clásico; >0 para un donut
    )
    st.plotly_chart(fig, use_container_width=True)

    # 10. Expositor de datos: región con máximo, mínimo y media global
    if not df_pie.empty:
        max_val = df_pie["Valor"].max()
        min_val = df_pie["Valor"].min()
        avg_val = df_pie["Valor"].mean()

        # Encontrar nombre de región con el máximo y el mínimo
        max_region = df_pie.loc[df_pie["Valor"].idxmax(), "COMARCA"]
        min_region = df_pie.loc[df_pie["Valor"].idxmin(), "COMARCA"]

        st.subheader("Estadísticas del Año Seleccionado")
        st.write(f"- **Región con Valor Máximo**: {max_region} ({max_val:.2f})")
        st.write(f"- **Región con Valor Mínimo**: {min_region} ({min_val:.2f})")
        st.write(f"- **Media de Todas las Regiones**: {avg_val:.2f}")
    else:
        st.warning("No hay datos disponibles para el año seleccionado.")

if __name__ == "__main__":
    main()
