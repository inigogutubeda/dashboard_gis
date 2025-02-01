import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

class TerritorialDataCollector:
    def __init__(self):
        # Define preguntas obligatorias
        self.mandatory_questions = [
            "¿Cuál es tu nombre completo?",
            "¿En qué organización trabajas?",
            "¿Cuál es tu rol?",
            "¿Qué plataformas utilizas para datos?",
            "¿Con qué frecuencia actualizas datos?",
            "¿Cuáles son tus fuentes principales?",
            "¿Qué herramientas de análisis usas?",
            "¿Cómo procesas la información?",
            "¿Qué indicadores son importantes?"
        ]
        self.mandatory_index = 0
        self.MAX_FOLLOW_UP = 1  # Límite de preguntas de seguimiento
        
        # Inicializa cliente OpenAI
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Configuración de almacenamiento
        self.data_path = Path("data/user_data")
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.json_file_path = self.data_path / "development_data.json"
        
        # Inicialización del estado de sesión
        self.init_session_state()

    def init_session_state(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "mandatory_index" not in st.session_state:
            st.session_state.mandatory_index = 0
        if "follow_up_count" not in st.session_state:
            st.session_state.follow_up_count = 0
        if "responses" not in st.session_state:
            st.session_state.responses = {}

    def get_ai_analysis(self, user_input, question):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en desarrollo territorial y análisis de datos."},
                    {"role": "user", "content": f"Analiza esta respuesta a '{question}': {user_input}"}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error en análisis AI: {e}")
            return None

    def process_response(self, user_input):
        index = st.session_state.mandatory_index
        question = self.mandatory_questions[index]

        if index not in st.session_state.responses:
            st.session_state.responses[question] = []

        ai_analysis = self.get_ai_analysis(user_input, question)
        
        st.session_state.responses[question].append({
            "respuesta": user_input,
            "análisis": ai_analysis
        })

        st.session_state.chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_analysis}
        ])

        # Control de preguntas de seguimiento
        if st.session_state.follow_up_count >= self.MAX_FOLLOW_UP:
            self.advance_question()
        else:
            st.session_state.follow_up_count += 1

    def advance_question(self):
        st.session_state.mandatory_index += 1
        st.session_state.follow_up_count = 0
        
        if st.session_state.mandatory_index >= len(self.mandatory_questions):
            st.session_state.mandatory_index = "completed"

    def save_data(self):
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "responses": st.session_state.responses
        }
        try:
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4, ensure_ascii=False)
            st.success("Datos guardados exitosamente.")
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")

# ----------------------------------------------------------------------------
# INTERFAZ STREAMLIT
# ----------------------------------------------------------------------------
def main():
    st.title("📊 Chat sobre Desarrollo Territorial")
    collector = TerritorialDataCollector()

    if st.session_state.mandatory_index != "completed":
        index = st.session_state.mandatory_index
        question = collector.mandatory_questions[index]
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        user_input = st.chat_input(f"📝 {question}")
        if user_input:
            collector.process_response(user_input)
            st.rerun()
    else:
        st.success("¡Gracias por completar el cuestionario!")
        if st.button("Descargar Respuestas"):
            collector.save_data()

if __name__ == "__main__":
    main()
