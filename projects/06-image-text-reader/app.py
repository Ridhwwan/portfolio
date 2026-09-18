"""Upload a photo containing text and extract readable text using Tesseract OCR."""

import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image


st.set_page_config(page_title="Image Text Reader", layout="centered")
st.title("Image Text Reader (OCR)")
st.write("Upload an image with text — printed signs, book pages, screenshots — and extract the text.")

preprocess = st.selectbox(
    "Preprocessing",
    ["None", "Grayscale + Threshold", "Grayscale + Blur", "Sharpen"],
    help="Preprocessing can improve accuracy on noisy or low-contrast images"
)

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = np.array(Image.open(uploaded))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # preprocess based on selection
    if preprocess == "Grayscale + Threshold":
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    elif preprocess == "Grayscale + Blur":
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        processed = cv2.medianBlur(gray, 3)
    elif preprocess == "Sharpen":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        processed = cv2.filter2D(img_bgr, -1, kernel)
    else:
        processed = img_bgr

    # run OCR
    with st.spinner("Reading text..."):
        text = pytesseract.image_to_string(processed)

        # also get bounding boxes for visualization
        boxes = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)

    st.image(img, caption="Original", use_container_width=True)

    # draw detected text regions
    annotated = img.copy()
    for i in range(len(boxes["text"])):
        if int(boxes["conf"][i]) > 40:  # confidence threshold
            x, y, w, h = boxes["left"][i], boxes["top"][i], boxes["width"][i], boxes["height"][i]
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)

    with st.expander("Show detected text regions"):
        st.image(annotated, use_container_width=True)

    st.subheader("Extracted Text")
    if text.strip():
        st.text_area("", text, height=200)
        st.download_button("Download as .txt", text, "extracted_text.txt", "text/plain")
    else:
        st.info("No text detected. Try a different preprocessing option.")
