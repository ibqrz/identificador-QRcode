import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

st.title("Dashboard de Visão Computacional")

uploaded = st.file_uploader("Envie uma imagem")

if uploaded:
    file_bytes = np.asarray(bytearray(uploaded.read()),
                            
    dtype=np.uint8)

    img = cv2.imdecode(file_bytes, 1)
    st.image(img, caption="Original", channels="BGR")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    st.image(gray, caption="Escala de Cinza")
    
    edges = cv2.Canny(gray, 100, 200)
    st.image(edges, caption="Bordas")
   
    # HISTOGRAMA
    fig, ax = plt.subplots()
    ax.hist(gray.ravel(), bins=256)
    ax.set_title("Histograma")
    st.pyplot(fig)