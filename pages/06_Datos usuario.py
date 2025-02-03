import streamlit as st
from utils.territorial_chat import TerritorialChat

# Añadir CSS personalizado para una interfaz más atractiva
st.markdown(
    """
    <style>
    .chat-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    .chat-history {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        max-height: 500px;
        overflow-y: auto;
    }
    .chat-message {
        margin-bottom: 12px;
    }
    .chat-message span {
        display: block;
    }
    .role-system { color: #7f8c8d; }
    .role-user { color: #2980b9; }
    .role-assistant { color: #27ae60; }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializar el chat en el estado de sesión
if "chat" not in st.session_state:
    st.session_state.chat = TerritorialChat()

st.markdown('<div class="chat-title">Chat - Desarrollo Territorial</div>', unsafe_allow_html=True)

# Usamos un formulario para enviar la respuesta (clear_on_submit limpia el input)
with st.form(key="chat_form", clear_on_submit=True):
    user_message = st.text_input("Escribe tu respuesta:")
    submitted = st.form_submit_button("Enviar")

if submitted and user_message:
    # Si aún no se ha registrado el nombre, se procesa la respuesta como nombre.
    if st.session_state.chat.user_name is None:
        st.session_state.chat.add_user_answer(user_message)
    else:
        st.session_state.chat.add_user_answer(user_message)
        # Control de seguimiento: si se ha alcanzado el máximo, avanzar a la siguiente pregunta.
        if st.session_state.chat.follow_up_count >= st.session_state.chat.MAX_FOLLOW_UP:
            st.session_state.chat.go_to_next_mandatory_question()
        else:
            st.session_state.chat.follow_up_count += 1
        # Se obtiene la respuesta del modelo para mostrarla en el historial.
        st.session_state.chat.get_model_response()

# Mostrar el historial de la conversación (omitimos mensajes intermedios que no sean relevantes si lo deseas)
st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for msg in st.session_state.chat.conversation_history:
    role = msg.get("role")
    content = msg.get("content")
    # Opcional: Puedes filtrar mensajes no deseados (por ejemplo, omitir forzados o instrucciones internas)
    if role == "system":
        st.markdown(f'<div class="chat-message role-system"><span><strong>Sistema:</strong> {content}</span></div>', unsafe_allow_html=True)
    elif role == "user":
        st.markdown(f'<div class="chat-message role-user"><span><strong>Usuario:</strong> {content}</span></div>', unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f'<div class="chat-message role-assistant"><span><strong>Asistente:</strong> {content}</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
