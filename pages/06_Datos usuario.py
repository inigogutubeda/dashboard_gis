import streamlit as st
from utils.territorial_chat import TerritorialChat

st.set_page_config(page_title="Chat Territorial", layout="wide")

# CSS mejorado para una apariencia más profesional
st.markdown("""
    <style>
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
        margin: 8px 0;
        padding: 10px;
        border-radius: 8px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        text-align: right;
        font-weight: bold;
        border-radius: 15px;
    }
    .assistant-message {
        background-color: #f1f1f1;
        text-align: left;
        border-radius: 15px;
    }
    .stTextInput>div>div>input {
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #ccc !important;
    }
    .stButton>button {
        background-color: #ff4757 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = TerritorialChat()

st.title("💬 Chat - Desarrollo Territorial")

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat.conversation_history:
    if msg["role"] == "system":
        continue  # 🔹 No mostramos el mensaje del sistema al usuario
    role_class = "user-message" if msg["role"] == "user" else "assistant-message"
    st.markdown(f'<div class="message {role_class}"><p>{msg["content"]}</p></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.chat.chat_complete:
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input("✍️ Escribe tu respuesta:")
        submitted = st.form_submit_button("📩 Enviar")

    if submitted and user_message:
        st.session_state.chat.add_user_answer(user_message)
        st.session_state.chat.get_model_response()

if st.session_state.chat.chat_complete:
    st.subheader("📢 ¿Te gustaría que un experto te contacte?")
    st.text_input("✏️ Nombre:")
    st.text_input("📧 Email:")
    st.selectbox("💼 Área de interés:", ["Desarrollo Territorial", "Economía", "Sostenibilidad", "Otro"])
    st.text_area("📝 Mensaje adicional:")
    st.button("✅ Enviar solicitud")
