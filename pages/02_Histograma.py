# pages/02_histograma.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Importamos las utilidades para carga y geoprocesado
from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import (
    prepare_geodata,
    detect_year_columns,
    convert_year_to_numeric
)

st.set_page_config(layout="wide")
# Añadimos un poco de CSS para mejorar la apariencia

def main():
    st.title("Histograma de evolución de datos por comarca (Comparación)")

    # 1. Cargar Shapefile
    try:
        gdf = load_shapefile("data/COMARCAS_5000_ETRS89.shp")
    except Exception as e:
        st.error(f"Error al leer el shapefile: {e}")
        st.stop()

    # 2. Seleccionar CSV
    csv_files = {
        "Porcentaje establecimeintos sector construccion (% sobre total)": "data/Porcentaje establecimientos sector construccion sobre el total.csv",
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

    # 5. Detectar columnas que representan años
    year_columns = detect_year_columns(gdf_merged)
    if not year_columns:
        st.warning("No se han detectado columnas de años en el CSV.")
        st.stop()

    # 6. Convertir todas las columnas de año a numérico
    for ycol in year_columns:
        gdf_merged = convert_year_to_numeric(gdf_merged, ycol)

    # 7. Seleccionar (multi) comarcas, hasta un máximo de 3
    regiones_disponibles = gdf_merged["COMARCA"].dropna().unique().tolist()
    seleccion_comarcas = st.sidebar.multiselect(
        "Selecciona una o varias comarcas (máx 3):",
        options=regiones_disponibles
    )

    # Controlar si se seleccionan más de 3
    if len(seleccion_comarcas) > 3:
        st.error("Solo puedes seleccionar hasta 3 comarcas a la vez.")
        st.stop()

    # Verificar que se ha seleccionado al menos 1
    if not seleccion_comarcas:
        st.info("Selecciona al menos una comarca en la barra lateral.")
        st.stop()

    # 8. Creamos un DataFrame "largo" (melt) para plotear las series de años
    #    Columns a mantener: "COMARCA", {todas las year_columns}
    #    Pasamos de wide a long: col "Año", col "Valor"
    df_plot_list = []
    for comarca in seleccion_comarcas:
        row_region = gdf_merged[gdf_merged["COMARCA"] == comarca]
        if row_region.empty:
            continue

        # Para cada columna de año, guardamos (comarca, año, valor)
        for col in year_columns:
            valor = row_region[col].values[0]  # la comarca aparece una vez en gdf_merged
            df_plot_list.append({
                "COMARCA": comarca,
                "Año": col,
                "Valor": valor
            })

    df_plot = pd.DataFrame(df_plot_list)

    # 9. Creamos el histograma (barras) con Plotly
    #    Cada comarca será una serie distinta (usando el color)
    fig = px.bar(
        df_plot,
        x="Año",
        y="Valor",
        color="COMARCA",
        barmode="group",
        title="Evolución de valores por comarca",
        template="plotly_white",
        labels={"Valor": csv_choice},
        text="Valor"  # Para que muestre el valor encima de cada barra
    )
    fig.update_layout(
        autosize=False,
        width=1500,  # Ajusta el ancho del gráfico
        height=600   # Ajusta la altura del gráfico si es necesario
    )
    # Ajustamos la posición del texto
    fig.update_traces(textposition="outside")

    # Presentamos el histograma
    st.plotly_chart(fig, use_container_width=True)

    # 10. Cálculo de estadísticas (media, mínimo y máximo) para cada comarca
    stats_data = []
    for comarca in seleccion_comarcas:
        # Filtramos
        sub = df_plot[df_plot["COMARCA"] == comarca]
        media_val = sub["Valor"].mean()
        min_val = sub["Valor"].min()
        max_val = sub["Valor"].max()
        stats_data.append({
            "Comarca": comarca,
            "Media": f"{media_val:.2f}",
            "Mínimo": f"{min_val:.2f}",
            "Máximo": f"{max_val:.2f}"
        })

    st.subheader("Estadísticas")
    # Mostramos en forma de tabla
    st.table(pd.DataFrame(stats_data))

    # 11. Recuadro o bloque con la "fuente de dato"
    st.info("""
    Datos obtenidos de: https://opendata.euskadi.eus/catalogo-datos/
    """)

if __name__ == "__main__":
    main()
