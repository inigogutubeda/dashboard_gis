import streamlit as st
from utils.territorial_chat import TerritorialChat

# CSS mejorado para la interfaz del chat
st.markdown(
    """
    <style>
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        max-height: 600px;
        overflow-y: auto;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .message {
        display: flex;
        align-items: center;
        margin: 10px 0;
    }
    .user-message {
        justify-content: flex-end;
        text-align: right;
    }
    .assistant-message {
        justify-content: flex-start;
        text-align: left;
    }
    .message p {
        padding: 12px;
        border-radius: 8px;
        max-width: 75%;
        margin: 5px;
        font-size: 14px;
    }
    .user-message p {
        background-color: #007bff;
        color: white;
    }
    .assistant-message p {
        background-color: #e9ecef;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Formulario de información inicial
if "user_info" not in st.session_state:
    with st.form("user_info_form"):
        nombre = st.text_input("Tu nombre:")
        region = st.text_input("¿En qué región trabajas?")
        sector = st.text_input("¿En qué sector trabajas?")
        enviado = st.form_submit_button("Iniciar Chat")

    if enviado and nombre:
        st.session_state.user_info = {
            "nombre": nombre,
            "region": region,
            "sector": sector
        }
        st.session_state.chat = TerritorialChat()
        st.session_state.chat.add_user_answer(nombre)
        st.experimental_rerun()

# Inicializar el chat si no está en sesión
if "chat" not in st.session_state:
    st.session_state.chat = TerritorialChat()

st.title("Chat - Desarrollo Territorial")
st.markdown("Utiliza el chat para aportar información complementaria. La respuesta se borrará al enviarla.")

# Renderizado del historial de conversación
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat.conversation_history:
        if msg["role"] == "system":
            continue
        elif msg["role"] == "user":
            st.markdown(
                f'<div class="message user-message"><p><strong>Tú:</strong> {msg["content"]}</p></div>',
                unsafe_allow_html=True,
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f'<div class="message assistant-message"><p><strong>Asistente:</strong> {msg["content"]}</p></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

# Entrada del usuario
with st.form(key="chat_form", clear_on_submit=True):
    user_message = st.text_input("Escribe tu respuesta:")
    submitted = st.form_submit_button("Enviar")

if submitted and user_message:
    st.session_state.chat.add_user_answer(user_message)
    response = st.session_state.chat.get_model_response()
    st.experimental_rerun()
