import streamlit as st
from utils.territorial_chat import TerritorialChat

# Configuración de la página con diseño mejorado
st.set_page_config(page_title="Chat Territorial", layout="wide")

# CSS mejorado para una apariencia moderna y atractiva
st.markdown(
    """
    <style>
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .chat-container {
        width: 80%;
        max-width: 800px;
        background-color: #ffffff;
        border-radius: 15px;
        padding: 15px;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ccc;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .message {
        display: flex;
        align-items: center;
        margin: 8px 0;
    }
    .user-message {
        justify-content: flex-end;
        text-align: right;
        color: white;
        background-color: #007bff;
        padding: 12px;
        border-radius: 15px;
        max-width: 75%;
    }
    .assistant-message {
        justify-content: flex-start;
        text-align: left;
        background-color: #f1f1f1;
        padding: 12px;
        border-radius: 15px;
        max-width: 75%;
    }
    .form-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        width: 100%;
        max-width: 600px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .stButton>button {
        background-color: #28a745;
        color: white;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Inicializar el chat si no está en sesión
if "chat" not in st.session_state:
    st.session_state.chat = TerritorialChat()
    st.session_state.chat_complete = False

st.markdown("<div class='header-container'><h2>💬 Chat - Desarrollo Territorial</h2></div>", unsafe_allow_html=True)

# Renderizado del historial de conversación con mejor estilo
display_messages = "<div class='chat-container'>"
for msg in st.session_state.chat.conversation_history:
    if msg["role"] == "system":
        continue
    elif msg["role"] == "user":
        display_messages += f"<div class='message user-message'><p>{msg["content"]}</p></div>"
    elif msg["role"] == "assistant":
        display_messages += f"<div class='message assistant-message'><p>{msg["content"]}</p></div>"
display_messages += "</div>"
st.markdown(display_messages, unsafe_allow_html=True)

# Entrada del usuario con control de preguntas obligatorias
if not st.session_state.chat_complete:
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input("✍️ Escribe tu respuesta:")
        submitted = st.form_submit_button("📩 Enviar")

    if submitted and user_message:
        st.session_state.chat.add_user_answer(user_message)
        
        if st.session_state.chat.mandatory_index < len(st.session_state.chat.mandatory_questions):
            next_question = st.session_state.chat.mandatory_questions[st.session_state.chat.mandatory_index]
            st.session_state.chat.conversation_history.append({"role": "assistant", "content": next_question})
            st.session_state.chat.mandatory_index += 1
        else:
            st.session_state.chat_complete = True
        st.rerun()

# Mostrar formulario de contacto una vez finalizado el chat
if st.session_state.chat_complete:
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("📢 ¿Te gustaría que un experto te contacte?")
        with st.form("contact_form"):
            nombre = st.text_input("✏️ Nombre:")
            email = st.text_input("📧 Email:")
            area_interes = st.selectbox("💼 Área de interés:", ["Desarrollo Territorial", "Economía", "Sostenibilidad", "Otro"])
            mensaje = st.text_area("📝 Mensaje adicional:")
            enviado = st.form_submit_button("✅ Enviar solicitud")
        
        if enviado and nombre and email:
            st.success("¡Gracias! Nos pondremos en contacto contigo pronto.")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
