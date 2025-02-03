import streamlit as st
from utils.territorial_chat import TerritorialChat

# Inicializar el chat si no existe en el estado de sesión
if "chat" not in st.session_state:
    st.session_state.chat = TerritorialChat()

st.title("Chat - Desarrollo Territorial")

# Campo de entrada para la respuesta del usuario en el chat
user_message = st.text_input("Escribe tu respuesta:")

if st.button("Enviar"):
    if user_message:
        st.session_state.chat.add_user_answer(user_message)
        if st.session_state.chat.follow_up_count >= st.session_state.chat.MAX_FOLLOW_UP:
            st.session_state.chat.go_to_next_mandatory_question()
        else:
            st.session_state.chat.follow_up_count += 1
        st.session_state.chat.get_model_response()

st.markdown("### Historial de la Conversación:")
for msg in st.session_state.chat.conversation_history:
    role = msg.get("role")
    content = msg.get("content")
    if role == "system":
        st.markdown(f"**Sistema:** {content}")
    elif role == "user":
        st.markdown(f"**Usuario:** {content}")
    elif role == "assistant":
        st.markdown(f"**Asistente:** {content}")
