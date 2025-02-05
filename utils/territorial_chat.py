import os
import json
from datetime import datetime
from openai import OpenAI
import streamlit as st

class TerritorialChat:
    """
    Clase que maneja el flujo de una conversación enfocada en desarrollo territorial.
    Se mantiene el uso de self.client = OpenAI(api_key=...) para la conexión con la API.
    """
    def __init__(self):
        # Se obtiene la API key desde los secretos de Streamlit Cloud.
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Nombre del usuario (se define tras la primera respuesta)
        self.user_name = None
        # Indica si todas las preguntas obligatorias ya fueron respondidas
        self.chat_complete = False

        # ----- PROMPTS Y CONTEXTO -----
        self.system_prompt = (
            "Eres un entrevistador experto en desarrollo territorial. "
            "Tu objetivo es recopilar información clave para aumentar la granularidad de los datos en este ámbito. "
            "Debes cubrir una serie de preguntas obligatorias para obtener datos cerrados, "
            "pero puedes hacer hasta 1 pregunta de seguimiento si detectas información relevante. "
            "Mantén la conversación centrada en temas de desarrollo territorial."
        )

        # Se inicia el historial con el prompt del sistema y un saludo inicial
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": "Hola, ¿cuál es tu nombre?"}
        ]

        # ----- PREGUNTAS OBLIGATORIAS -----
        self.mandatory_questions = [
            "¿Cuáles consideras que son los principales desafíos que enfrenta tu región en términos de desarrollo territorial?",
            "¿En qué empresas has trabajado?",
            "¿Qué KPIs consideras relevantes en tu sector?",
            "¿Dónde consultas tus fuentes de información?"
        ]
        self.mandatory_index = 0  # Índice para saber en cuál pregunta obligatoria estamos

        # Control para preguntas de seguimiento
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 2  # máximo de 1 pregunta de seguimiento por pregunta obligatoria

        # Diccionario donde se guardan las respuestas del usuario
        self.collected_data = {}

        # Ruta del archivo JSON donde se guardará la información al final
        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")

    def add_user_answer(self, user_input: str):
        """
        Procesa la respuesta del usuario en el flujo de la conversación.
        - Si aún no se tiene el nombre del usuario, se guarda y lanza la primera pregunta obligatoria.
        - Si se está en preguntas obligatorias, se guarda la respuesta y se decide si hacer pregunta de seguimiento.
        - Si ya no hay más preguntas, se marca el chat como completo.
        """
        user_input = user_input.strip()
        self.conversation_history.append({"role": "user", "content": user_input})

        if self.user_name is None:
            self.user_name = user_input
            self.collected_data["Nombre"] = self.user_name
            self.ask_next_mandatory_question()
            return

        if self.mandatory_index < len(self.mandatory_questions):
            current_question = self.mandatory_questions[self.mandatory_index]
            self.collected_data.setdefault(current_question, []).append(user_input)

            if self.follow_up_count < self.MAX_FOLLOW_UP:
                follow_up_question = self.generate_follow_up_question(user_input)
                if follow_up_question:
                    self.conversation_history.append({"role": "assistant", "content": follow_up_question})
                    self.follow_up_count += 1
                    return

            # Añadir mensaje de transición antes de la siguiente pregunta obligatoria
            self.add_transition_message()

            self.mandatory_index += 1
            self.follow_up_count = 0
            self.ask_next_mandatory_question()
        else:
            self.chat_complete = True
            self.conversation_history.append({"role": "assistant", "content": "¡Gracias! Hemos terminado la entrevista."})

    def ask_next_mandatory_question(self):
        """
        Muestra la siguiente pregunta obligatoria si aún quedan pendientes.
        Si no, indica que la entrevista ha terminado.
        """
        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            self.conversation_history.append({"role": "assistant", "content": next_question})
        else:
            self.chat_complete = True
            self.conversation_history.append({"role": "assistant", "content": "¡Gracias! Hemos terminado con las preguntas obligatorias."})

    def generate_follow_up_question(self, user_input: str):
        """
        Genera una pregunta de seguimiento basada en la respuesta del usuario.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un entrevistador experto en desarrollo territorial. "
                            "Tu tarea es formular UNA sola pregunta de seguimiento concisa y clara "
                            "basada en la respuesta del usuario, para profundizar en detalles relevantes."
                        )
                    },
                    {"role": "user", "content": user_input}
                ]
            )
            return completion.choices[0].message.content
        except Exception:
            return None

    def add_transition_message(self):
        """
        Agrega un mensaje antes de pasar a la siguiente pregunta obligatoria para mejorar la UX.
        """
        transition_message = "Gracias por tu respuesta. Ahora procederemos a la siguiente pregunta obligatoria."
        self.conversation_history.append({"role": "assistant", "content": transition_message})

    def save_data_to_json(self):
        """
        Guarda la sesión actual (fecha y datos recopilados) en un archivo JSON.
        """
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "territorial_info": self.collected_data
        }
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            else:
                existing_data = []

            existing_data.append(new_entry)
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)

            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)

            st.success(f"Datos guardados en {self.json_file_path}")
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
