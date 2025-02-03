import streamlit as st
from utils.territorial_chat import TerritorialChat

# CSS para mejorar el diseño del chat
def apply_chat_styles():
    st.markdown(
        """
        <style>
        .chat-container {
            background-color: #ffffff;
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 8px;
            max-height: 600px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
        .message { margin: 10px 0; }
        .user-message { text-align: right; }
        .assistant-message { text-align: left; }
        .message p {
            display: inline-block;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            margin: 0;
        }
        .user-message p { background-color: #d1e7dd; color: #0f5132; }
        .assistant-message p { background-color: #e2e3e5; color: #41464b; }
        </style>
        """,
        unsafe_allow_html=True
    )

# Inicializar chat si no existe
if "chat" not in st.session_state:
    st.session_state.chat = TerritorialChat()

# Aplicar estilos y título
apply_chat_styles()
st.title("Chat - Desarrollo Territorial")
st.markdown("Utiliza el chat para aportar información complementaria. La respuesta se borrará al enviarla.")

# Mostrar historial de conversación
def display_chat_history():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat.conversation_history:
        if msg["role"] == "system":
            continue  # Omitimos mensajes de sistema
        css_class = "user-message" if msg["role"] == "user" else "assistant-message"
        st.markdown(f'<div class="message {css_class}"><p><strong>{"Tú" if msg["role"] == "user" else "Asistente"}:</strong> {msg["content"]}</p></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

display_chat_history()

# Formulario de entrada de texto
with st.form(key="chat_form", clear_on_submit=True):
    user_message = st.text_input("Escribe tu respuesta:")
    submitted = st.form_submit_button("Enviar")

if submitted and user_message:
    response = st.session_state.chat.add_user_answer(user_message)
    response_text = st.session_state.chat.get_model_response()
    if response_text:
        st.session_state.chat.conversation_history.append({"role": "assistant", "content": response_text})
    st.experimental_rerun()
