"""Convert any photo into a pencil sketch, watercolor, or cartoon using OpenCV."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io


def pencil_sketch(img_bgr, blur_strength=21):
    """Convert to pencil sketch using edge-division technique."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(inverted, (blur_strength, blur_strength), 0)
    sketch = cv2.divide(gray, cv2.bitwise_not(blurred), scale=256)
    return sketch


def watercolor(img_bgr):
    """Create a watercolor effect using bilateral filtering."""
    # bilateral filter smooths while preserving edges
    color = cv2.bilateralFilter(img_bgr, d=9, sigmaColor=200, sigmaSpace=200)
    # apply multiple times for stronger effect
    for _ in range(3):
        color = cv2.bilateralFilter(color, d=9, sigmaColor=200, sigmaSpace=200)
    return color


def cartoon(img_bgr):
    """Create a cartoon effect: smooth color + bold edges."""
    # get edges
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, blockSize=9, C=2
    )
    # smooth colors
    color = cv2.bilateralFilter(img_bgr, d=9, sigmaColor=300, sigmaSpace=300)
    # combine: color where edges are white, black where edges are black
    cartoon_img = cv2.bitwise_and(color, color, mask=edges)
    return cartoon_img


def emboss(img_bgr):
    """Apply an emboss filter."""
    kernel = np.array([[-2, -1, 0],
                       [-1,  1, 1],
                       [ 0,  1, 2]])
    return cv2.filter2D(img_bgr, -1, kernel) + 128


st.set_page_config(page_title="Photo to Art", layout="centered")
st.title("Photo → Art Converter")
st.write("Upload a photo and transform it into different artistic styles.")

style = st.selectbox("Choose a style", ["Pencil Sketch", "Watercolor", "Cartoon", "Emboss"])

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = np.array(Image.open(uploaded))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    with st.spinner(f"Applying {style} effect..."):
        if style == "Pencil Sketch":
            result = pencil_sketch(img_bgr)
            is_gray = True
        elif style == "Watercolor":
            result = cv2.cvtColor(watercolor(img_bgr), cv2.COLOR_BGR2RGB)
            is_gray = False
        elif style == "Cartoon":
            result = cv2.cvtColor(cartoon(img_bgr), cv2.COLOR_BGR2RGB)
            is_gray = False
        elif style == "Emboss":
            result = cv2.cvtColor(emboss(img_bgr), cv2.COLOR_BGR2RGB)
            is_gray = False

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original", use_container_width=True)
    with col2:
        st.image(result, caption=style, use_container_width=True)

    # download
    if is_gray:
        result_pil = Image.fromarray(result)
    else:
        result_pil = Image.fromarray(result)

    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    st.download_button(f"Download {style.lower()}", buf.getvalue(), f"{style.lower().replace(' ', '_')}.png", "image/png")

