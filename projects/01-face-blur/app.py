"""Upload a photo and automatically blur all detected faces for privacy."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Face Blur", layout="centered")
st.title("Face Blur for Privacy")
st.write("Upload a photo — all detected faces will be blurred automatically.")

# OpenCV ships with pre-trained Haar cascade models (open source, no download needed)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

blur_strength = st.slider("Blur strength", 10, 100, 51, step=2)

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    # load image
    img = np.array(Image.open(uploaded))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # blur each face region
    for (x, y, w, h) in faces:
        face_region = img_bgr[y:y+h, x:x+w]
        blurred = cv2.GaussianBlur(face_region, (blur_strength, blur_strength), 0)
        img_bgr[y:y+h, x:x+w] = blurred

    # convert back for display
    result = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption=f"Original ({len(faces)} face(s) found)", use_container_width=True)
    with col2:
        st.image(result, caption="Blurred", use_container_width=True)

    # download button
    result_pil = Image.fromarray(result)
    import io
    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    st.download_button("Download blurred image", buf.getvalue(), "blurred.png", "image/png")

