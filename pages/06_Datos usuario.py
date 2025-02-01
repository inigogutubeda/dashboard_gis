import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

st.set_page_config(
    page_title="Análisis Territorial",
    page_icon="🗺️",
    layout="wide"
)

class TerritorialDataCollector:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Initialize session state
        if "territorial_chat_history" not in st.session_state:
            st.session_state.territorial_chat_history = []
        if "mandatory_index" not in st.session_state:
            st.session_state.mandatory_index = 0
        if "collected_data" not in st.session_state:
            st.session_state.collected_data = {}

        # Questions for territorial development
        self.mandatory_questions = [
            "¿Qué región o territorio está analizando?",
            "¿Cuál es el principal sector económico de la región?",
            "¿Cuál es la tasa de desempleo actual en la región?",
            "¿Qué infraestructuras críticas necesitan mejora?",
            "¿Cuál es el nivel medio de renta per cápita?",
            "¿Qué porcentaje de empresas son PYMES?",
            "¿Cuáles son los principales proyectos de desarrollo actuales?",
            "¿Qué indicadores de innovación destacan?",
            "¿Cuál es el nivel de digitalización empresarial?",
            "¿Qué fondos europeos/públicos se están utilizando?"
        ]

        # Setup data storage
        self.data_path = Path("data/territorial_data")
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.json_file_path = self.data_path / "territorial_indicators.json"

    def get_assistant_response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error en la comunicación con OpenAI: {e}")
            return None

    def store_user_answer(self, user_input):
        try:
            current_question = self.mandatory_questions[st.session_state.mandatory_index]
            
            if current_question not in st.session_state.collected_data:
                st.session_state.collected_data[current_question] = []
            st.session_state.collected_data[current_question].append(user_input)
            
            st.session_state.territorial_chat_history.append({
                "role": "user",
                "content": user_input
            })
            return True
        except Exception as e:
            st.error(f"Error almacenando respuesta: {e}")
            return False

    def save_data_to_json(self):
        try:
            new_session = {
                "timestamp": datetime.now().isoformat(),
                "territory": st.session_state.collected_data.get(
                    "¿Qué región o territorio está analizando?", [""])[0],
                "indicators": st.session_state.collected_data
            }

            existing_data = []
            if self.json_file_path.exists():
                with open(self.json_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]

            existing_data.append(new_session)
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            
            st.success("Datos territoriales guardados correctamente")
            return True
        except Exception as e:
            st.error(f"Error guardando datos: {e}")
            return False

def main():
    st.title("🗺️ Análisis de Desarrollo Territorial")
    
    st.markdown("""
    Este módulo recopila información sobre indicadores territoriales para análisis 
    de desarrollo económico y social. Los datos serán utilizados para generar 
    insights sobre el desarrollo regional.
    """)

    collector = TerritorialDataCollector()

    # Chat interface
    st.subheader("💬 Cuestionario Territorial")

    # Display chat history
    for message in st.session_state.territorial_chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Check if there are more questions
    if st.session_state.mandatory_index < len(collector.mandatory_questions):
        current_question = collector.mandatory_questions[st.session_state.mandatory_index]
        
        # Display input box
        user_input = st.chat_input(f"Responde a: {current_question}")
        
        if user_input:
            # Show user input
            with st.chat_message("user"):
                st.write(user_input)

            # Store answer
            collector.store_user_answer(user_input)

            # Get AI response
            system_prompt = """Eres un experto en desarrollo territorial y análisis económico regional.
            Analiza la respuesta del usuario y proporciona insights relevantes."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analiza esta respuesta a '{current_question}': {user_input}"}
            ]
            
            ai_response = collector.get_assistant_response(messages)
            if ai_response:
                with st.chat_message("assistant"):
                    st.write(ai_response)
                st.session_state.territorial_chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })

            # Move to next question
            st.session_state.mandatory_index += 1
            st.rerun()
    else:
        st.success("¡Has completado todas las preguntas! Gracias por tu participación.")
        collector.save_data_to_json()
        
        # Add download button for JSON data
        if collector.json_file_path.exists():
            with open(collector.json_file_path, "r", encoding="utf-8") as f:
                data = f.read()
            st.download_button(
                label="Descargar datos en formato JSON",
                data=data,
                file_name="territorial_indicators.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()