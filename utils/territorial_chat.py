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
        self.user_region = None  # Nueva variable para región
        self.user_sector = None  # Nueva variable para sector

        # ----- PROMPTS Y CONTEXTO -----
        self.system_prompt = (
            "Eres un entrevistador experto en desarrollo territorial. "
            "Tu objetivo es recopilar información clave para aumentar la granularidad de los datos en este ámbito. "
            "Debes cubrir una serie de preguntas obligatorias para obtener datos cerrados, "
            "pero puedes hacer hasta 1 pregunta de seguimiento (más abierta) por cada pregunta obligatoria si identificas "
            "que hay información interesante adicional. Mantén la conversación centrada en temas de desarrollo territorial."
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
        self.MAX_FOLLOW_UP = 1
        
        # Donde se guardarán las respuestas del usuario
        self.collected_data = {}
        
        # Ruta del archivo JSON para guardar la sesión
        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")
    
    def add_user_answer(self, user_input: str):
        """
        Procesa la respuesta del usuario. Si aún no se ha registrado el nombre, se asume que el
        primer mensaje es su nombre y se genera una respuesta automática de saludo y la primera pregunta.
        """
        if self.user_name is None:
            self.user_name = user_input.strip()
            self.collected_data["Nombre"] = [self.user_name]
            self.conversation_history.append({"role": "user", "content": user_input})
            saludo = (f"Encantado de conocerte, {self.user_name}. Vamos a empezar con la primera pregunta: "
                      f"{self.mandatory_questions[0]}")
            self.conversation_history.append({"role": "assistant", "content": saludo})
            return saludo
        else:
            if self.mandatory_index < len(self.mandatory_questions):
                current_question = self.mandatory_questions[self.mandatory_index]
            else:
                current_question = f"Pregunta fuera de índice_{self.mandatory_index}"
            
            self.collected_data.setdefault(current_question, []).append(user_input)
            self.conversation_history.append({"role": "user", "content": user_input})

    def go_to_next_mandatory_question(self):
        """Avanza a la siguiente pregunta obligatoria."""
        self.mandatory_index += 1
        self.follow_up_count = 0  # Resetea el contador
        
        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            self.conversation_history.append({"role": "assistant", "content": next_question})
        else:
            self.conversation_history.append({"role": "assistant", "content": "No hay más preguntas obligatorias."})
    
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
