import streamlit as st
import zxcvbn  # Importa la librería zxcvbn
from Interpretar import predict_class, get_response, intents
import time

# Función para analizar la fortaleza de la contraseña usando zxcvbn
def analyze_password_strength(password):
    result = zxcvbn.zxcvbn(password)  # Evaluar la contraseña usando la función correcta
    score = result['score']  # Obtener la puntuación de fortaleza de la contraseña

    # La puntuación de zxcvbn varía entre 0 (débil) y 4 (fuerte)
    if score == 0:
        return "Muy débil", "red", "🔴"
    elif score == 1:
        return "Débil", "orange", "🟠"
    elif score == 2:
        return "Moderada", "yellow", "🟡"
    elif score == 3:
        return "Fuerte", "green", "🟢"
    else:
        return "Muy fuerte", "blue", "🔵"

# Inicializar variables de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "awaiting_password" not in st.session_state:
    st.session_state.awaiting_password = False

if "password_prompt" not in st.session_state:
    st.session_state.password_prompt = ""  # Para manejar mensajes relacionados con la contraseña

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Mensaje inicial del asistente
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Hola, ¿cómo puedo ayudarte?")
    st.session_state.messages.append({"role": "assistant", "content": "Hola, ¿cómo puedo ayudarte?"})

# Si estamos esperando una contraseña
if st.session_state.awaiting_password:
    password = st.text_input("Ingresa tu contraseña para analizarla:", type="password")
    if password:  # Cuando el usuario escribe la contraseña
        # Analizar la fortaleza de la contraseña
        with st.spinner("Analizando la fortaleza de tu contraseña..."):
            time.sleep(2)  # Espera simulada de 2 segundos
            strength, color, emoji = analyze_password_strength(password)

        # Mostrar el resultado con diseño atractivo y centrado
        response = f"<div style='text-align:center; margin-top:20px;'>"
        response += f"<h3 style='color:{color}; font-size:24px;'>Tu contraseña es {strength} {emoji}</h3>"
        response += "<p>Recuerda usar contraseñas largas y únicas para mayor seguridad.</p>"
        response += "</div>"

        # Mostrar el resultado
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)
        
        # Agregar el mensaje al historial
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Restablecer el estado para permitir nuevas preguntas
        st.session_state.awaiting_password = False
        st.session_state.password_prompt = ""  # Limpiar el prompt de contraseña
        st.rerun()
else:
    # Entrada de texto para el usuario
    if prompt := st.chat_input("¿Cómo puedo ayudarte?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Verificar si el modelo espera una contraseña
        if st.session_state.password_prompt:
            st.session_state.awaiting_password = True
            response = st.session_state.password_prompt
            st.session_state.password_prompt = ""  # Limpiar después de mostrar
        else:
            # Simular "cargando" antes de procesar la respuesta
            with st.spinner("Procesando tu solicitud..."):
                time.sleep(2)  # Espera simulada de 2 segundos
                intents_list = predict_class(prompt)
                response = get_response(intents_list, intents)

            # Comprobar si la respuesta solicita una contraseña
            if "verificacion_revision_contraseña" in response:
                st.session_state.password_prompt = "Por favor, ingresa tu contraseña para analizarla:"
                st.session_state.awaiting_password = True
                st.rerun()

            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
