# pages/04_bubble_chart.py

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import (
    prepare_geodata,
    detect_year_columns,
    convert_year_to_numeric
)

st.set_page_config(layout="wide")

def main():
    st.title("Bubble Chart: Evolución por Año y Comparación de Regiones")

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

    # 5. Detectar columnas de años
    year_columns = detect_year_columns(gdf_merged)
    if not year_columns:
        st.warning("No se han detectado columnas de años en el CSV.")
        st.stop()

    # 6. Convertimos todas las columnas de año a numérico
    for ycol in year_columns:
        gdf_merged = convert_year_to_numeric(gdf_merged, ycol)

    # 7. Construimos un DF "largo" (Año, Valor, COMARCA)
    df_bubble_list = []
    for idx, row in gdf_merged.iterrows():
        comarca_name = row["COMARCA"]
        for col in year_columns:
            val = row[col]
            df_bubble_list.append({
                "COMARCA": comarca_name,
                "Año": int(col),  # Convertimos col (string) a int para el eje X
                "Valor": val
            })

    df_bubble = pd.DataFrame(df_bubble_list)

    # 8. Selección de comarcas (primera opción = "Todas")
    regiones_disponibles = sorted(df_bubble["COMARCA"].dropna().unique().tolist())
    seleccion = st.sidebar.multiselect(
        "Selecciona las comarcas (o 'Todas'):",
        options=["Todas"] + regiones_disponibles,
        default=["Todas"]
    )

    # Si "Todas" está en la lista, usamos todas las regiones
    if "Todas" in seleccion:
        regiones_filtradas = regiones_disponibles
    else:
        regiones_filtradas = seleccion

    # 9. Filtramos el DataFrame por las comarcas elegidas
    df_filtrado = df_bubble[df_bubble["COMARCA"].isin(regiones_filtradas)]

    # 10. Creamos el bubble chart con Plotly
    #     - x = Año, y = Valor, color = COMARCA, size = Valor
    fig = px.scatter(
        df_filtrado,
        x="Año",
        y="Valor",
        color="COMARCA",
        size="Valor",
        hover_data=["COMARCA"],
        title=f"Bubble Chart: {csv_choice}",
        labels={"Valor": csv_choice},
        height=600
    )
    # Ajustes opcionales
    fig.update_layout(
        xaxis=dict(tickmode="linear"),  # Para que muestre todos los años en secuencia
        margin={"r":20,"t":40,"l":40,"b":20}
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("Selecciona múltiples comarcas para compararlas o elige 'Todas' para ver el conjunto completo.")

if __name__ == "__main__":
    main()
