import streamlit as st

def main():
    # Opcional: Define un título de la página y un ícono en la pestaña del navegador
    st.set_page_config(
        page_title="Home - Dashboard Interactivo",
        page_icon="🗺️",
        layout="wide"
    )

    # Muestra el logo (ajusta la ruta y ancho/alto a tu gusto)
    st.image("UrgegiLogo.png", width=400)

    # Título principal
    st.title("¡Bienvenido a la App GIS & Dashboard!")

    # Subtítulo o descripción rápida
    st.markdown("""
    **Esta es la página principal (Home).**  
    Utiliza el menú de la izquierda para navegar a las distintas secciones:
    - **Gráficos** (incluye Bubble chart, Diagrama de Queso, Histograma y Tablas)
    - **Mapa** interactivo
    - **Datos de usuario** (para introducir y guardar información)
    """)

    # Sección "¿Qué ofrece esta app?"
    st.markdown("""
    ---
    ### ¿Qué ofrece esta aplicación?
    - **Visualizaciones interactivas** de datos geográficos y estadísticos.
    - **Mapas** para explorar la información por comarcas.
    - **Dashboards** con gráficos dinámicos para comparar distintos indicadores.
    - **Formulario** de recolección de datos para que los usuarios aporten información.
    
    Nuestro objetivo es **facilitar la toma de decisiones** a través de 
    una interfaz clara y amigable.
    ---
    """)

    # Ejemplo de dos columnas para resaltar algo
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Instrucciones principales")
        st.markdown("""
        1. Selecciona la **sección** que quieras explorar en el menú lateral.
        2. Filtra los datos según el **año** o el **tipo de indicador**.
        3. Haz clic en los elementos de las gráficas o mapas para ver detalles.
        4. En el apartado de **Datos de Usuario**, introduce información y envíala para su registro.
        """)
    
    st.write("---")
    st.write("¡Explora nuestras secciones y saca el máximo partido al *Dashboard Interactivo*!")

if __name__ == "__main__":
    main()
