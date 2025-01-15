import streamlit as st
import pandas as pd
# from utils import load_data  # Ejemplo de import de una función auxiliar

def main():
    st.title("Dashboard: Indicadores de Desarrollo Territorial y Emprendimiento")
    
    st.write("Bienvenido a nuestro MVP con Streamlit.")
    
    # Aquí podemos tener un sidebar o menús de navegación
    st.sidebar.title("Navegación")
    opciones = ["Inicio", "Indicadores", "Datos GIS"]
    eleccion = st.sidebar.radio("Ir a:", opciones)
    
    if eleccion == "Inicio":
        st.subheader("Página de Inicio")
        st.write("Explicación general, objetivos del dashboard, etc.")
    
    elif eleccion == "Indicadores":
        st.subheader("Indicadores de Desarrollo")
        st.write("Aquí presentaremos tablas, gráficas, etc.")

    elif eleccion == "Datos GIS":
        st.subheader("Mapas e Información Geográfica")
        st.write("Aquí podremos integrar mapas interactivos o datos con coordenadas.")
    
if __name__ == "__main__":
    main()
