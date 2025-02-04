import os
import json
from datetime import datetime
from openai import OpenAI
import streamlit as st

class TerritorialChat:
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        self.user_name = None
        self.chat_complete = False  

        self.system_prompt = (
            "Eres un entrevistador experto en desarrollo territorial. "
            "Tu objetivo es recopilar información clave para aumentar la granularidad de los datos en este ámbito. "
            "Debes cubrir una serie de preguntas obligatorias para obtener datos cerrados, "
            "pero puedes hacer hasta 1 pregunta de seguimiento si detectas información relevante. "
            "Mantén la conversación centrada en temas de desarrollo territorial."
        )
        
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},  
        ]
        
        self.mandatory_questions = [
            "¿Cuáles consideras que son los principales desafíos que enfrenta tu región en términos de desarrollo territorial?",
            "¿En qué empresas has trabajado?",
            "¿Qué KPIs consideras relevantes en tu sector?",
            "¿Dónde consultas tus fuentes de información?"
        ]
        
        self.mandatory_index = 0  
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 1  

        self.collected_data = {}

        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")

        # 🔹 Iniciar conversación sin el mensaje del sistema en la interfaz
        self.conversation_history.append({"role": "assistant", "content": "Hola, ¿cuál es tu nombre?"})
    
    def add_user_answer(self, user_input: str):
        self.conversation_history.append({"role": "user", "content": user_input})

        if self.user_name is None:
            self.user_name = user_input.strip()
            self.collected_data["Nombre"] = [self.user_name]
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

                self.mandatory_index += 1  
                self.follow_up_count = 0  
                self.ask_next_mandatory_question()
            else:
                self.chat_complete = True  
    
    def ask_next_mandatory_question(self):
        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            self.conversation_history.append({"role": "assistant", "content": next_question})
        else:
            self.conversation_history.append({"role": "assistant", "content": "¡Gracias! Hemos terminado con las preguntas obligatorias."})
            self.chat_complete = True
    
    def generate_follow_up_question(self, user_input):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Genera una única pregunta de seguimiento para obtener más detalles sobre la siguiente respuesta:"},
                    {"role": "user", "content": user_input}
                ]
            )
            return completion.choices[0].message.content
        except Exception:
            return None
    
    def get_model_response(self):
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
