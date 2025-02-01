import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()

class TerritorialChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Prompt inicial de sistema
        self.system_prompt = (
            "Eres un experto en desarrollo territorial y análisis de datos. "
            "Debes hacer preguntas clave sobre la metodología de análisis, plataformas utilizadas y "
            "fuentes de información. Puedes hacer hasta 2 preguntas libres de seguimiento en cada una."
        )

        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Hola, inicia la conversación sobre análisis territorial."},
        ]

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
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 1
        self.collected_data = {}
        self.json_file_path = os.path.join("data", "user_data", "development_data.json")

    def run_chat(self):
        st.title("📊 Chat sobre Desarrollo Territorial")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "mandatory_index" not in st.session_state:
            st.session_state.mandatory_index = 0

        if "follow_up_count" not in st.session_state:
            st.session_state.follow_up_count = 0

        if "responses" not in st.session_state:
            st.session_state.responses = {}

        self._display_chat()

    def _display_chat(self):
        index = st.session_state.mandatory_index
        if index < len(self.mandatory_questions):
            question = self.mandatory_questions[index]
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            user_input = st.chat_input(f"📝 {question}")
            if user_input:
                self._store_user_answer(user_input)
                self._stream_model_response()
                st.rerun()
        else:
            st.success("¡Gracias por completar el cuestionario!")
            if st.button("Descargar Respuestas"):
                self._save_data_to_json()

    def _store_user_answer(self, user_input):
        index = st.session_state.mandatory_index
        question = self.mandatory_questions[index]
        
        if question not in st.session_state.responses:
            st.session_state.responses[question] = []
        
        st.session_state.responses[question].append(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        if st.session_state.follow_up_count >= self.MAX_FOLLOW_UP:
            self._go_to_next_question()
        else:
            st.session_state.follow_up_count += 1

    def _go_to_next_question(self):
        st.session_state.mandatory_index += 1
        st.session_state.follow_up_count = 0
        if st.session_state.mandatory_index >= len(self.mandatory_questions):
            st.session_state.mandatory_index = "completed"

    def _stream_model_response(self):
        try:
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + st.session_state.chat_history
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )
            full_response = ""
            with st.chat_message("assistant"):
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        st.write(chunk.choices[0].delta.content)
            
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error en el streaming de la respuesta: {e}")

    def _save_data_to_json(self):
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

if __name__ == "__main__":
    chat = TerritorialChat()
    chat.run_chat()
