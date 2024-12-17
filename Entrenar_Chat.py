import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import random

# Cargar datos
data_file = open('intents_contraseñas.json', 'r', encoding='utf-8').read()
intents = json.loads(data_file)

lemmatizer = WordNetLemmatizer()

words = []
classes = []
documents = []
ignore_words = ['?', '!']

# Recorre cada intención y sus patrones en el archivo JSON
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Tokeniza las palabras en cada patrón y las agrega a la lista de palabras
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        # Agrega el par (patrón, etiqueta) a la lista de documentos
        documents.append((w, intent['tag']))
        # Si la etiqueta no está en la lista de clases, la agrega
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Lematiza las palabras y las convierte en minúsculas, excluyendo las palabras ignoradas
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

# Guarda las listas de palabras y clases en archivos pickle
pickle.dump(words, open('Palabras.pkl', 'wb'))
pickle.dump(classes, open('Clases.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

# Crea el conjunto de entrenamiento
for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    for word in words:
        # Crea una bolsa de palabras binaria para cada patrón
        bag.append(1) if word in pattern_words else bag.append(0)
    output_row = list(output_empty)
    # Crea un vector de salida con un 1 en la posición correspondiente a la etiqueta de la intención
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

# Mezcla aleatoriamente el conjunto de entrenamiento
random.shuffle(training)

# Divide el conjunto de entrenamiento en características (train_x) y etiquetas (train_y)
train_x = [row[0] for row in training]
train_y = [row[1] for row in training]

train_x = np.array(train_x)
train_y = np.array(train_y)

# Crea el modelo de red neuronal con más complejidad utilizando el enfoque adecuado para la entrada
input_layer = Input(shape=(len(train_x[0]),))  # Usamos Input en lugar de input_shape
x = Dense(256, activation='relu')(input_layer)
x = Dropout(0.5)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(64, activation='relu')(x)
output_layer = Dense(len(train_y[0]), activation='softmax')(x)

# Crear el modelo usando el Input explícito
model = Model(inputs=input_layer, outputs=output_layer)

# Configura el optimizador Adam
model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])

# Configura EarlyStopping para evitar el sobreentrenamiento (detiene el entrenamiento si no mejora)
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Entrena el modelo con el conjunto de entrenamiento y validación (validación con 10% del conjunto de datos)
hist = model.fit(np.array(train_x), np.array(train_y), epochs=300, batch_size=10, verbose=1, validation_split=0.1, callbacks=[early_stopping])

# Guarda el modelo entrenado en un archivo .keras
model.save('Red_Modelo_Chat.keras')

print("Modelo creado")
