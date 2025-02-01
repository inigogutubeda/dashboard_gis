import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

class TerritorialDataCollector:
    def __init__(self):
        # Initialize OpenAI client with secret
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        if "territorial_chat_history" not in st.session_state:
            st.session_state.territorial_chat_history = []
        if "mandatory_index" not in st.session_state:
            st.session_state.mandatory_index = 0
        if "collected_data" not in st.session_state:
            st.session_state.collected_data = {}

        # Updated questions for territorial development
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
        data_path = Path("data/territorial_data")
        data_path.mkdir(parents=True, exist_ok=True)
        self.json_file_path = data_path / "territorial_indicators.json"

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

    def save_data_to_json(self):
        new_session = {
            "timestamp": datetime.now().isoformat(),
            "territory": st.session_state.collected_data.get("¿Qué región o territorio está analizando?", [""])[0],
            "indicators": st.session_state.collected_data,
            "metadata": {
                "data_source": "user_input",
                "collection_method": "interactive_survey",
                "version": "1.0"
            }
        }

        try:
            existing_data = []
            if self.json_file_path.exists():
                with open(self.json_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            
            existing_data.append(new_session)
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            
            st.success("Datos territoriales guardados correctamente")
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")

def main():
    st.title("📊 Análisis de Desarrollo Territorial")
    st.markdown("""
    Este módulo recopila información sobre indicadores territoriales para análisis 
    de desarrollo económico y social. Los datos serán utilizados para generar 
    insights sobre el desarrollo regional.
    """)

    collector = TerritorialDataCollector()

    # Display chat interface
    for message in st.session_state.territorial_chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.mandatory_index < len(collector.mandatory_questions):
        current_question = collector.mandatory_questions[st.session_state.mandatory_index]
        
        user_input = st.chat_input(f"Responde a: {current_question}")
        
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            collector.store_user_answer(user_input)
            
            analysis_prompt = f"Analiza esta respuesta sobre '{current_question}' desde una perspectiva de desarrollo territorial y sugiere áreas de mejora si es relevante."
            
            messages = [
                {"role": "system", "content": "Eres un experto en desarrollo territorial y análisis económico regional."},
                {"role": "user", "content": f"{analysis_prompt}\nRespuesta: {user_input}"}
            ]
            
            ai_response = collector.get_assistant_response(messages)
            if ai_response:
                with st.chat_message("assistant"):
                    st.write(ai_response)
                st.session_state.territorial_chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })

            st.session_state.mandatory_index += 1
            st.rerun()
    else:
        st.success("¡Análisis territorial completado! Los datos han sido registrados.")
        collector.save_data_to_json()

if __name__ == "__main__":
    main()