import streamlit as st
import pandas as pd
import plotly.express as px

# Importamos las utilidades para carga y geoprocesado
from utils.data_loader import load_shapefile, load_csv
from utils.geoutils import prepare_geodata, detect_year_columns, convert_year_to_numeric

def main():
    st.title("Histograma de evolución de datos por comarca")

    # 1. Cargar Shapefile
    try:
        gdf = load_shapefile("data/COMARCAS_5000_ETRS89.shp")
    except Exception as e:
        st.error(f"Error al leer el shapefile: {e}")
        st.stop()

    # 2. Seleccionar CSV (en la barra lateral, igual que en el mapa)
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

    # 7. Seleccionar comarca (en la barra lateral a la derecha)
    #    Añade 'key' si quieres que aparezca el selector en la derecha (beta_feature).
    #    De lo contrario, lo normal es que aparezca a la izquierda igual que el selectbox anterior.
    regiones_disponibles = gdf_merged["COMARCA"].dropna().unique().tolist()
    region_seleccionada = st.sidebar.selectbox("Selecciona la comarca:", options=regiones_disponibles)

    # 8. Filtramos los datos de la comarca elegida (suponiendo que cada 'COMARCA' aparece solo una vez)
    row_region = gdf_merged[gdf_merged["COMARCA"] == region_seleccionada]

    # 9. Construimos un DataFrame auxiliar con dos columnas: "Año" y "Valor"
    #    para poder plotear la evolución
    year_values = []
    if not row_region.empty:
        for col in year_columns:
            valor = row_region[col].values[0]  # tomamos el primer (y único) valor
            year_values.append({"Año": col, "Valor": valor})
    else:
        st.warning(f"No se encontró información para la comarca: {region_seleccionada}")
        return

    df_plot = pd.DataFrame(year_values)

    # 10. Crear el histograma (Bar Chart) con Plotly
    fig = px.bar(
        df_plot,
        x="Año",
        y="Valor",
        title=f"Evolución de {csv_choice} en {region_seleccionada}",
        labels={"Año": "Año", "Valor": csv_choice}
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
