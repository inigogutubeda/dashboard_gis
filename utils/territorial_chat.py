import os
import json
from datetime import datetime
from openai import OpenAI
import streamlit as st

class TerritorialChat:
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.user_name = None
        self.system_prompt = (
            "Eres un entrevistador experto en desarrollo territorial. "
            "Recopila información clave con preguntas obligatorias y preguntas de seguimiento limitadas."
        )
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": "Hola, ¿cuál es tu nombre?"}
        ]
        self.mandatory_questions = [
            "¿Cuáles son los principales desafíos en tu región?",
            "¿En qué empresas has trabajado?",
            "¿Qué KPIs consideras relevantes en tu sector?",
            "¿Dónde consultas tus fuentes de información?"
        ]
        self.mandatory_index = 0
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 1
        self.collected_data = {}
        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")

    def add_user_answer(self, user_input: str):
        if self.user_name is None:
            self.user_name = user_input.strip()
            self.collected_data["Nombre"] = [self.user_name]
            self.conversation_history.append({"role": "user", "content": user_input})
            greeting = f"Encantado, {self.user_name}. {self.mandatory_questions[0]}"
            self.conversation_history.append({"role": "assistant", "content": greeting})
            return greeting
        else:
            if self.mandatory_index < len(self.mandatory_questions):
                question = self.mandatory_questions[self.mandatory_index]
                self.collected_data.setdefault(question, []).append(user_input)
                self.conversation_history.append({"role": "user", "content": user_input})
                self.go_to_next_mandatory_question()

    def go_to_next_mandatory_question(self):
        self.mandatory_index += 1
        self.follow_up_count = 0
        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            self.conversation_history.append({"role": "assistant", "content": next_question})
        else:
            self.conversation_history.append({"role": "assistant", "content": "No hay más preguntas obligatorias."})

    def get_model_response(self):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history
            )
            response = completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            return f"Error en la API: {e}"

    def save_data_to_json(self):
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "territorial_info": self.collected_data
        }
        try:
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
            with open(self.json_file_path, "a", encoding="utf-8") as f:
                json.dump(new_entry, f, indent=4, ensure_ascii=False)
                f.write("\n")
            st.success("Datos guardados correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")

