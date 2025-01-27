# pages/05_tablas.py

import streamlit as st
import pandas as pd
from utils.data_loader import load_csv

st.set_page_config(layout="wide")

def main():
    st.title("Tablas de Datos")

    # Diccionario de CSV disponibles
    csv_files = {
        "Porcentaje establecimeintos sector construccion (% sobre total)": "data/Porcentaje establecimientos sector construccion sobre el total.csv",        "Contratos Indefinidos": "data/Contratos indefinidos registrados en el ano (% total contratos).csv",
        "Contratos Anuales": "data/Contratos registrados en el ano ( habitantes).csv",
        "Densidad comercial minorista": "data/Densidad comercial minorista ( habitantes).csv",
        "Empleo generado microempresas": "data/Empleo generado por las microempresas (0-9 empleados) (%).csv",
        "Indice rotación contractual": "data/Indice de rotacion contractual (contratos_personas).csv",
        "Población contratada año": "data/Poblacion contratada en el ano ( habitantes).csv",
        "Mayor 16 años. Sector servicios": "data/Poblacion de 16 y mas anos ocupada en el sector servicios (%).csv"
        # Agrega los que necesites
    }

    # Selector para elegir la tabla
    csv_choice = st.sidebar.selectbox(
        "Elige la tabla que deseas visualizar:",
        list(csv_files.keys())
    )

    st.write(f"Has seleccionado la tabla: **{csv_choice}**")

    chosen_csv = csv_files[csv_choice]

    # Cargar el CSV y mostrarlo
    try:
        df = load_csv(chosen_csv)
    except Exception as e:
        st.error(f"Error al leer {chosen_csv}: {e}")
        st.stop()

    st.dataframe(df)

    st.info("Puedes hacer scroll en la tabla para ver todas las filas y columnas.")

if __name__ == "__main__":
    main()
