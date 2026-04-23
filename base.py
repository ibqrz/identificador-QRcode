# importacao

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten,
Dense

# carregar dataset

(x_train, y_train), (x_test, y_test) = mnist.load_data()
print("Treino:", x_train.shape)
print("Teste:", x_test.shape)

# normalização

x_train = x_train / 255.0
x_test = x_test / 255.0

# ajustar dimensão (CNN)

x_train = x_train.reshape(-1,28,28,1)
x_test = x_test.reshape(-1,28,28,1)

# criar modelo CNN

model = Sequential([
Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
MaxPooling2D(),
Conv2D(64, (3,3), activation='relu'),
MaxPooling2D(),
Flatten(),
Dense(128, activation='relu'),
Dense(10, activation='softmax')
])


# compilar modelo

model.compile(
optimizer='adam',
loss='sparse_categorical_crossentropy',
metrics=['accuracy']
)

# treinar modelo

model.fit(x_train, y_train, epochs=3)

# avaliação

loss, acc = model.evaluate(x_test, y_test)
print("Acurácia:", acc)


# predição

img = x_test[0]
plt.imshow(img.reshape(28,28), cmap='gray')
plt.title("Imagem de entrada")
plt.show()
pred = model.predict(img.reshape(1,28,28,1))
print("Classe prevista:", np.argmax(pred))
print("Classe real:", y_test[0])