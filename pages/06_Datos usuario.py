import streamlit as st
import openai
import os
import pandas as pd
from datetime import datetime

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class TerritorialBot:
    def __init__(self):
        self.init_session_state()
        self.questions = {
            "identification": {
                "questions": ["¿Cuál es tu nombre?", "¿En qué organización trabajas?"],
                "context": "Recopilación de información básica del usuario"
            },
            "data_sources": {
                "questions": ["¿Qué fuentes de datos utilizas?", "¿Con qué frecuencia actualizas tus datos?"],
                "context": "Entender las fuentes de información del usuario"
            },
            "territorial": {
                "questions": ["¿Qué región analizas?", "¿Qué indicadores son más relevantes para tu trabajo?"],
                "context": "Comprender el enfoque territorial"
            }
        }

    def init_session_state(self):
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'current_category' not in st.session_state:
            st.session_state.current_category = "identification"
        if 'question_index' not in st.session_state:
            st.session_state.question_index = 0
        if 'responses' not in st.session_state:
            st.session_state.responses = {}

    def get_ai_response(self, user_input, context):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Eres un experto en desarrollo territorial. Contexto: {context}"},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Error en la comunicación con OpenAI: {str(e)}"

    def process_response(self, user_input):
        current_category = st.session_state.current_category
        current_context = self.questions[current_category]["context"]
        
        # Get AI analysis
        ai_response = self.get_ai_response(user_input, current_context)
        
        # Store responses
        st.session_state.responses[f"{current_category}_{st.session_state.question_index}"] = {
            "question": self.questions[current_category]["questions"][st.session_state.question_index],
            "answer": user_input,
            "ai_analysis": ai_response
        }
        
        # Update chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Move to next question
        self.advance_question()

    def advance_question(self):
        current_category = st.session_state.current_category
        if st.session_state.question_index < len(self.questions[current_category]["questions"]) - 1:
            st.session_state.question_index += 1
        else:
            # Move to next category
            categories = list(self.questions.keys())
            current_index = categories.index(current_category)
            if current_index < len(categories) - 1:
                st.session_state.current_category = categories[current_index + 1]
                st.session_state.question_index = 0
            else:
                st.session_state.current_category = "completed"

def main():
    st.title("🤖 Asistente de Desarrollo Territorial")
    
    bot = TerritorialBot()
    
    if st.session_state.current_category != "completed":
        current_category = st.session_state.current_category
        current_question = bot.questions[current_category]["questions"][st.session_state.question_index]
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Get user input
        user_input = st.chat_input(f"📝 {current_question}")
        if user_input:
            bot.process_response(user_input)
    else:
        st.success("¡Gracias por completar el cuestionario!")
        if st.button("Descargar Respuestas"):
            df = pd.DataFrame.from_dict(st.session_state.responses, orient='index')
            df.to_csv(f"respuestas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            st.success("Respuestas guardadas exitosamente!")

if __name__ == "__main__":
    main()