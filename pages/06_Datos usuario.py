import streamlit as st
from utils.territorial_chat import TerritorialChat

# Configuración de la página
st.set_page_config(
    page_title="Chat Territorial Avanzado",
    page_icon=":earth_americas:",
    layout="wide"
)

# CSS personalizado para mejorar la apariencia del chat
CUSTOM_CSS = """
<style>
    .chat-box {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ccc;
        border-radius: 15px;
        background-color: #ffffff;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        width: fit-content;
        max-width: 80%;
    }
    .assistant-bubble {
        background-color: #f0f2f6;
        text-align: left;
        margin-right: auto;
    }
    .user-bubble {
        background-color: #2b6af9;
        color: white;
        text-align: right;
        margin-left: auto;
    }
    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #2b6af9 0%, #28a745 100%);
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Inicializar la instancia de chat en la sesión
if "chat" not in st.session_state:
    st.session_state["chat"] = TerritorialChat()

chat_instance = st.session_state["chat"]

st.title("💬 Chat Territorial Avanzado")

st.write(
    "Bienvenido(a). Este chat te guiará por una serie de preguntas obligatorias "
    "para recopilar información sobre el desarrollo territorial. "
    "Podrás profundizar con preguntas de seguimiento en caso de que el sistema "
    "considere necesario más detalles."
)

# =========================
# BARRA DE PROGRESO
# =========================
num_questions = len(chat_instance.mandatory_questions)
current_index = chat_instance.mandatory_index

if num_questions > 0:
    progress_percent = (current_index / num_questions) * 100
else:
    progress_percent = 100

st.markdown("#### Progreso de la Entrevista")
st.markdown(
    f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_percent}%;"></div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# SECCIÓN DE CHAT
# =========================
st.markdown("### Conversación")
with st.container():
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in chat_instance.conversation_history:
        if msg["role"] == "system":
            continue
        bubble_class = "assistant-bubble" if msg["role"] == "assistant" else "user-bubble"
        st.markdown(
            f'<div class="chat-bubble {bubble_class}">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CONTROLES PARA RESPUESTAS DEL USUARIO
# =========================
if not chat_instance.chat_complete:
    def submit():
        user_response = st.session_state.user_input
        if user_response.strip():
            chat_instance.add_user_answer(user_response)
        st.session_state.user_input = ""  # Limpiar el campo de entrada

    st.text_input(
        "Escribe aquí tu respuesta:",
        key="user_input",
        on_change=submit
    )
else:
    st.success("¡Has completado todas las preguntas obligatorias!")

# =========================
# FORMULARIO FINAL (Contacto)
# =========================
if chat_instance.chat_complete:
    st.markdown("#### Formulario de Contacto")
    with st.form("contact_form"):
        contact_name = st.text_input("Nombre:")
        contact_email = st.text_input("Correo:")
        interest_area = st.selectbox(
            "Área de interés",
            ["Desarrollo Territorial", "Economía", "Sostenibilidad", "Otro"]
        )
        additional_msg = st.text_area("Mensaje adicional:")

        submitted = st.form_submit_button("Enviar Solicitud")
        if submitted:
            st.write("**Gracias. Pronto nos pondremos en contacto contigo.**")
            # Aquí podrías almacenar estos datos en tu clase o en alguna base de datos, e.g.:
            # chat_instance.save_contact_info(contact_name, contact_email, interest_area, additional_msg)

# =========================
# BOTONES DE GUARDADO / REINICIO
# =========================
st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button("Guardar datos recopilados en JSON"):
        chat_instance.save_data_to_json()

with col2:
    if st.button("Reiniciar Chat"):
        # Eliminamos la instancia del estado para arrancar desde cero
        st.session_state.pop("chat", None)
        # No llamamos a experimental_rerun(), simplemente la app se vuelve a
        # ejecutar y, al no encontrar "chat" en session_state,
        # creará una instancia nueva.
