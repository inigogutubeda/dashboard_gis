import os
import json
from datetime import datetime
from openai import OpenAI
import streamlit as st

class TerritorialChat:
    def __init__(self):
        # Se obtiene la API key desde los secrets de Streamlit Cloud
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # ----- PROMPTS Y CONTEXTO -----
        self.system_prompt = (
            "Eres un entrevistador experto en desarrollo territorial. "
            "Tu objetivo es recopilar información clave para aumentar la granularidad de los datos en este ámbito. "
            "Debes cubrir una serie de preguntas obligatorias para obtener datos cerrados, "
            "pero puedes hacer hasta 1 pregunta de seguimiento (más abierta) por cada pregunta obligatoria si identificas "
            "que hay información interesante adicional. Mantén la conversación centrada en temas de desarrollo territorial."
        )
        
        # Historial de la conversación para mantener el contexto
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                "Hola. Eres un entrevistador en desarrollo territorial. "
                "Empieza haciendo la primera pregunta obligatoria sobre el tema."
            )}
        ]

        # ----- PREGUNTAS OBLIGATORIAS (DESARROLLO TERRITORIAL) -----
        self.mandatory_questions = [
            "¿En qué sector trabajas?",
            "¿En qué empresas has trabajado?",
            "¿Qué KPIs consideras relevantes en tu sector?",
            "¿Dónde consultas tus fuentes de información?"
        ]

        # Índice para saber qué pregunta obligatoria se está trabajando
        self.mandatory_index = 0

        # Seguimiento de preguntas de seguimiento (máximo 1 por pregunta obligatoria)
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 1

        # Donde se guardarán las respuestas del usuario, asociadas a cada pregunta obligatoria
        self.collected_data = {}

        # Ruta del archivo JSON para guardar la sesión
        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")

    def add_user_answer(self, user_input: str):
        """
        Guarda la respuesta del usuario en 'collected_data' asociada a la pregunta obligatoria actual
        y añade el mensaje al historial.
        """
        if self.mandatory_index < len(self.mandatory_questions):
            current_question = self.mandatory_questions[self.mandatory_index]
        else:
            current_question = f"Pregunta fuera de índice_{self.mandatory_index}"
        
        self.collected_data.setdefault(current_question, [])
        self.collected_data[current_question].append(user_input)
        self.conversation_history.append({"role": "user", "content": user_input})
    
    def go_to_next_mandatory_question(self):
        """
        Avanza a la siguiente pregunta obligatoria y reinicia el contador de seguimiento.
        Añade un mensaje 'user' para forzar al modelo a formular la siguiente pregunta obligatoria.
        """
        self.mandatory_index += 1
        self.follow_up_count = 0  # Resetea el contador de seguimiento

        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            forced_prompt = (
                f"Por favor, pregunta: '{next_question}'. "
                "Recuerda que es una pregunta obligatoria y no te desvíes de momento."
            )
            self.conversation_history.append({"role": "user", "content": forced_prompt})
        else:
            self.conversation_history.append({
                "role": "user",
                "content": "Ya no hay más preguntas obligatorias. Puedes finalizar la conversación."
            })
    
    def get_model_response(self):
        """
        Realiza la llamada sincrónica a la API de OpenAI y retorna la respuesta completa.
        Se utiliza la estructura básica de los docs, sin streaming.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",  # Ajusta el modelo según tus necesidades.
                messages=self.conversation_history
            )
            response_message = completion.choices[0].message.content
            # Añadir la respuesta del asistente al historial para mantener el contexto
            self.conversation_history.append({"role": "assistant", "content": response_message})
            return response_message
        except Exception as e:
            return f"Error al obtener la respuesta del modelo: {e}"
    
    def save_data_to_json(self):
        """
        Guarda en un archivo JSON la sesión actual, incluyendo un timestamp y las respuestas recopiladas.
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
            st.success(f"Datos de la conversación guardados en {self.json_file_path}")
        except Exception as e:
            st.error(f"Error al guardar datos en JSON: {e}")
