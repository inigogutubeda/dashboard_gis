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
        # Índice para saber en cuál pregunta obligatoria estamos
        self.mandatory_index = 0

        # Control para preguntas de seguimiento
        self.follow_up_count = 0
        self.MAX_FOLLOW_UP = 1  # máximo de 1 pregunta de seguimiento por pregunta obligatoria

        # Diccionario donde se guardan las respuestas del usuario
        self.collected_data = {}

        # Ruta del archivo JSON donde se guardará la información al final
        # Puedes adaptar la ruta según tu estructura o parametrizarla
        self.json_file_path = os.path.join("data", "json_folder", "territorial_data.json")

    def add_user_answer(self, user_input: str):
        """
        Procesa la respuesta del usuario en el flujo de la conversación.
          - Si aún no se tiene el nombre del usuario, se guarda y lanza la primera pregunta obligatoria.
          - Si se está en preguntas obligatorias, se guarda la respuesta y se decide si hacer pregunta de seguimiento.
          - Si ya no hay más preguntas, se marca el chat como completo.
        """
        user_input = user_input.strip()
        
        # Registramos la respuesta del usuario en el historial
        self.conversation_history.append({"role": "user", "content": user_input})

        # 1) Si no tenemos todavía el nombre del usuario, lo guardamos
        if self.user_name is None:
            self.user_name = user_input
            # Guardamos el nombre como string o lista, a tu preferencia
            self.collected_data["Nombre"] = self.user_name
            # Después de guardar el nombre, lanzamos la primera pregunta obligatoria
            self.ask_next_mandatory_question()
            return

        # 2) Flujo de preguntas obligatorias
        if self.mandatory_index < len(self.mandatory_questions):
            current_question = self.mandatory_questions[self.mandatory_index]
            # Almacenamos la respuesta en un array por si hubiera varios intentos
            self.collected_data.setdefault(current_question, []).append(user_input)

            # Intentamos generar una pregunta de seguimiento (si no llegamos al límite)
            if self.follow_up_count < self.MAX_FOLLOW_UP:
                follow_up_question = self.generate_follow_up_question(user_input)
                if follow_up_question:
                    self.conversation_history.append({"role": "assistant", "content": follow_up_question})
                    self.follow_up_count += 1
                    # Terminamos aquí para esperar la respuesta a la pregunta de seguimiento
                    return

            # Si no se generó pregunta de seguimiento, o ya llegamos al límite
            # pasamos a la siguiente pregunta obligatoria
            self.mandatory_index += 1
            self.follow_up_count = 0  # Reiniciamos el conteo de follow-ups
            self.ask_next_mandatory_question()

        else:
            # No hay más preguntas obligatorias
            self.chat_complete = True

    def ask_next_mandatory_question(self):
        """
        Muestra la siguiente pregunta obligatoria si aún quedan pendientes.
        Si no, indica que la entrevista ha terminado.
        """
        if self.mandatory_index < len(self.mandatory_questions):
            next_question = self.mandatory_questions[self.mandatory_index]
            self.conversation_history.append({"role": "assistant", "content": next_question})
        else:
            # Si no hay más preguntas, marcamos la conversación como completa
            self.conversation_history.append(
                {"role": "assistant", "content": "¡Gracias! Hemos terminado con las preguntas obligatorias."}
            )
            self.chat_complete = True

    def generate_follow_up_question(self, user_input: str):
        """
        Genera una pregunta de seguimiento (hasta 1 por cada pregunta obligatoria),
        usando el contenido de la respuesta del usuario como contexto.
        Retorna la pregunta generada o None si no puede obtenerse.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",  # Asegúrate de que este modelo exista o ajusta según tus necesidades
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
        except Exception as e:
            # Podrías usar st.error(...) aquí también, pero lo normal es retornar None
            return None

    def get_model_response(self):
        """
        (Opcional) Genera una respuesta completa del modelo usando todo el historial.
        En tu flujo actual, no es imprescindible, pero sirve si deseas obtener una
        respuesta del asistente en base a la conversación previa.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",  # Ajusta si es necesario
                messages=self.conversation_history
            )
            response_message = completion.choices[0].message.content
            # Agregamos la respuesta al historial
            self.conversation_history.append({"role": "assistant", "content": response_message})
            return response_message
        except Exception as e:
            return f"Error al obtener respuesta del modelo: {e}"

    def save_data_to_json(self):
        """
        Guarda la sesión actual (fecha y datos recopilados) en un archivo JSON.
        En caso de que el archivo no exista, se crea. Si ya existe, se agrega
        una nueva entrada a la lista.
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

            # Añadimos la nueva entrada a la lista
            existing_data.append(new_entry)

            # Creamos el directorio si no existe
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)

            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)

            st.success(f"Datos guardados en {self.json_file_path}")
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
