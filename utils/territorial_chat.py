import os
import json
from datetime import datetime
from openai import OpenAI
import streamlit as st

class TerritorialChat:
    def __init__(self):
        # Se obtiene la API key desde los secretos de Streamlit Cloud.
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        self.user_name = None  # Se guardará el nombre del usuario
        self.chat_complete = False  # Bandera para saber cuándo finalizar el chat
        
        # ----- PROMPTS Y CONTEXTO -----
        self.system_prompt = (
            "Eres un entrevistador experto en desarrollo territorial. "
            "Tu objetivo es recopilar información clave para aumentar la granularidad de los datos en este ámbito. "
            "Debes cubrir una serie de preguntas obligatorias para obtener datos cerrados, "
            "pero puedes hacer hasta 1 pregunta de seguimiento si detectas información relevante. "
            "Mantén la conversación centrada en temas de desarrollo territorial."
        )
        
        # Se inicia el historial con el prompt del sistema
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
        
        self.mandatory_index = 0  # Índice de pregunta actual
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 1  # Límite de preguntas de seguimiento por cada pregunta obligatoria
        
        # Donde se guardarán las respuestas del usuario
        self.collected_data = {}
        
        # Ruta del archivo JSON para guardar la sesión
        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")
    
    def add_user_answer(self, user_input: str):
        """
        Procesa la respuesta del usuario. Si aún no se ha registrado el nombre, lo asigna y lanza la primera pregunta obligatoria.
        """
        if self.user_name is None:
            self.user_name = user_input.strip()
            self.collected_data["Nombre"] = [self.user_name]
            self.conversation_history.append({"role": "user", "content": user_input})
            self.ask_next_mandatory_question()
        else:
            if self.mandatory_index < len(self.mandatory_questions):
                current_question = self.mandatory_questions[self.mandatory_index]
                self.collected_data.setdefault(current_question, []).append(user_input)
                
                if self.follow_up_count < self.MAX_FOLLOW_UP:
                    follow_up_question = self.generate_follow_up_question(user_input)
                    if follow_up_question:
                        self.conversation_history.append({"role": "assistant", "content": follow_up_question})
                        self.follow_up_count += 1
                        return
                
                self.mandatory_index += 1  # Avanzar a la siguiente pregunta
                self.follow_up_count = 0  # Reiniciar contador de preguntas de seguimiento
                self.ask_next_mandatory_question()
            else:
                self.chat_complete = True  # Se han completado todas las preguntas
        
    def ask_next_mandatory_question(self):
        """Presenta la siguiente pregunta obligatoria si hay más pendientes."""
        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            self.conversation_history.append({"role": "assistant", "content": next_question})
        else:
            self.conversation_history.append({"role": "assistant", "content": "¡Gracias! Hemos terminado con las preguntas obligatorias."})
            self.chat_complete = True
    
    def generate_follow_up_question(self, user_input):
        """Genera una pregunta de seguimiento basada en la respuesta del usuario para mayor granularidad."""
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Genera una única pregunta de seguimiento para obtener más detalles sobre la siguiente respuesta:"},
                    {"role": "user", "content": user_input}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return None
    
    def get_model_response(self):
        """Genera una respuesta de OpenAI."""
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history
            )
            response_message = completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": response_message})
            return response_message
        except Exception as e:
            return f"Error al obtener respuesta del modelo: {e}"
    
    def save_data_to_json(self):
        """Guarda la sesión actual en JSON."""
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
