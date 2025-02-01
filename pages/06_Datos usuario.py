import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

class UserDataCollector:
    def __init__(self):
        # Define questions first
        self.questions = {
            "identification": [
                "¿Cuál es tu nombre completo?",
                "¿En qué organización trabajas?",
                "¿Cuál es tu rol?"
            ],
            "data_sources": [
                "¿Qué plataformas utilizas para datos?",
                "¿Con qué frecuencia actualizas datos?",
                "¿Cuáles son tus fuentes principales?"
            ],
            "methodology": [
                "¿Qué herramientas de análisis usas?",
                "¿Cómo procesas la información?",
                "¿Qué indicadores son importantes?"
            ]
        }

        # Initialize OpenAI client
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Setup storage
        self.data_path = Path("data/user_data")
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.json_file_path = self.data_path / "user_responses.json"
        
        # Initialize session state last
        self.init_session_state()

    def init_session_state(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "current_category" not in st.session_state:
            st.session_state.current_category = "identification"
        if "question_index" not in st.session_state:
            st.session_state.question_index = 0
        if "responses" not in st.session_state:
            st.session_state.responses = {}

    def get_ai_analysis(self, user_input, question):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis territorial y datos."},
                    {"role": "user", "content": f"Analiza esta respuesta a '{question}': {user_input}"}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error en análisis AI: {e}")
            return None

    def process_response(self, user_input):
        current_cat = st.session_state.current_category
        current_q = self.questions[current_cat][st.session_state.question_index]
        
        if current_cat not in st.session_state.responses:
            st.session_state.responses[current_cat] = {}
        
        ai_analysis = self.get_ai_analysis(user_input, current_q)
        
        st.session_state.responses[current_cat][current_q] = {
            "respuesta": user_input,
            "análisis": ai_analysis
        }

        st.session_state.chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_analysis}
        ])

        self.advance_question()

    def advance_question(self):
        current_cat = st.session_state.current_category
        if st.session_state.question_index < len(self.questions[current_cat]) - 1:
            st.session_state.question_index += 1
        else:
            categories = list(self.questions.keys())
            current_index = categories.index(current_cat)
            if current_index < len(categories) - 1:
                st.session_state.current_category = categories[current_index + 1]
                st.session_state.question_index = 0
            else:
                st.session_state.current_category = "completed"

def main():
    st.title("📊 Recopilación de Datos de Usuario")
    
    collector = UserDataCollector()
    
    if st.session_state.current_category != "completed":
        current_cat = st.session_state.current_category
        current_q = collector.questions[current_cat][st.session_state.question_index]
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        user_input = st.chat_input(f"📝 {current_q}")
        if user_input:
            collector.process_response(user_input)
            st.rerun()
    else:
        st.success("¡Gracias por completar el cuestionario!")
        if st.button("Descargar Respuestas"):
            with open(collector.json_file_path, "w", encoding="utf-8") as f:
                json.dump(st.session_state.responses, f, indent=4, ensure_ascii=False)
            st.success("Respuestas guardadas exitosamente!")

if __name__ == "__main__":
    main()