# pages/03_recogida_datos.py

import streamlit as st
import os
import json
import re
from datetime import datetime

def validate_phone(phone: str) -> bool:
    """Devuelve True si 'phone' contiene solo dígitos."""
    return phone.isdigit()

def validate_email(email: str) -> bool:
    """Validación sencilla de formato de email usando regex."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def main():
    st.title("Formulario de Recogida de Datos")

    st.write("Completa los campos y pulsa **Enviar** para guardar tu información.")
    
    # Puedes personalizar las industrias que quieras en la lista:
    INDUSTRIAS = ["Finanzas", "Tecnología", "Educación", "Salud", "Retail", "Otro"]

    # Formulario
    with st.form("form_datos"):
        nombre_completo = st.text_input("Nombre completo")
        telefono = st.text_input("Número de teléfono")
        email = st.text_input("Email")
        url_info = st.text_input("URL donde está localizada la información")
        industria = st.selectbox("Industria", options=INDUSTRIAS)
        texto_plano = st.text_area("Texto plano (describe lo que quieras)")

        # Botón de envío
        enviado = st.form_submit_button("Enviar")

        if enviado:
            # 1. Validaciones mínimas
            valid = True

            if not telefono.strip():
                st.error("El número de teléfono es obligatorio.")
                valid = False
            elif not validate_phone(telefono):
                st.error("El teléfono debe contener solo dígitos.")
                valid = False

            if not email.strip():
                st.error("El email es obligatorio.")
                valid = False
            elif not validate_email(email):
                st.error("El email no parece tener un formato válido.")
                valid = False

            # Puedes agregar más validaciones (nombre_completo no vacío, etc.)
            if not nombre_completo.strip():
                st.error("El nombre completo es obligatorio.")
                valid = False

            # 2. Si pasa todas las validaciones, guardamos en un JSON nuevo
            if valid:
                data_entry = {
                    "nombre_completo": nombre_completo,
                    "telefono": telefono,
                    "email": email,
                    "url_info": url_info,
                    "industria": industria,
                    "texto_plano": texto_plano,
                    "timestamp": str(datetime.now())
                }

                # Montamos un nombre único de archivo, por ej: usuarios_20250122_153045.json
                filename = f"usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                json_path = os.path.join("bucket", filename)

                # Aseguramos que la carpeta bucket/ exista
                os.makedirs(os.path.dirname(json_path), exist_ok=True)

                # Guardamos el diccionario en un JSON "nuevo"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data_entry, f, ensure_ascii=False, indent=4)

                # Confirmación
                st.success(f"¡Datos guardados!")

                # Forzamos un reinicio de la app para limpiar el formulario
                st.session_state["nombre_completo"] = ""
                st.session_state["telefono"] = ""
                st.session_state["email"] = ""
                st.session_state["url_info"] = ""
                st.session_state["industria"] = "Finanzas"  # valor por defecto
                st.session_state["texto_plano"] = ""

if __name__ == "__main__":
    main()
