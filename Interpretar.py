import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import secrets
import string
import time
import streamlit as st

# Inicialización
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents_contraseñas.json', 'r', encoding='utf-8').read())
words = pickle.load(open('Palabras.pkl', 'rb'))
classes = pickle.load(open('Clases.pkl', 'rb'))
model = load_model('Red_Modelo_Chat.keras')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    print(f"Procesando la sentencia: {sentence}")
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.6
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    print("Resultados de la predicción:", results)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def generar_contraseña_segura(longitud=12):
    """Genera una contraseña segura utilizando la biblioteca 'secrets'."""
    if longitud < 8:  # Contraseñas deben tener al menos 8 caracteres para ser seguras
        longitud = 8
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contraseña = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return contraseña

def get_response(intents_list, intents_json):
    if intents_list:  # Verifica si hay al menos un resultado de intención
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                if tag == "crear_contraseña_segura":
                    # Simular "cargando" antes de generar la contraseña
                    with st.spinner("Generando tu contraseña segura..."):
                        time.sleep(2)  # Espera simulada de 2 segundos
                        nueva_contraseña = generar_contraseña_segura()

                    # Presentación visual
                    result = (
                        "🔐 **Tu contraseña segura ha sido generada con éxito:**\n\n"
                        f"<p style='color:green; font-size:18px; font-weight:bold;'>{nueva_contraseña}</p>\n\n"
                        "✅ **Recuerda:** Guarda esta contraseña en un lugar seguro o utiliza un administrador de contraseñas."
                    )
                elif tag == "verificacion_revision_contraseña":
                    # Si la intención es validar una contraseña, se devuelve una respuesta especial
                    result = "verificacion_revision_contraseña"
                else:
                    result = random.choice(i['responses'])
                break
    else:
        result = "Lo siento, no puedo entender tu pregunta. ¿Podrías intentar de nuevo?"
    
    return result