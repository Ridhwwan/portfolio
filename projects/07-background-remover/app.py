"""Upload a photo and remove its background using the rembg library (U2-Net model, open source)."""

import streamlit as st
import numpy as np
from PIL import Image
from rembg import remove
import io


st.set_page_config(page_title="Background Remover", layout="centered")
st.title("Background Remover")
st.write("Upload a photo and get a transparent-background version. Uses the open-source U2-Net model.")

bg_choice = st.radio(
    "Output background",
    ["Transparent (PNG)", "White", "Custom color"],
    horizontal=True
)

custom_color = None
if bg_choice == "Custom color":
    custom_color = st.color_picker("Pick a background color", "#000000")

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = Image.open(uploaded)

    with st.spinner("Removing background... (first run downloads the model)"):
        # rembg uses U2-Net — fully open source, no API key needed
        result = remove(img)

    # apply background choice
    if bg_choice == "White":
        bg = Image.new("RGBA", result.size, (255, 255, 255, 255))
        bg.paste(result, mask=result.split()[3])
        result = bg.convert("RGB")
        fmt = "JPEG"
        ext = "jpg"
    elif bg_choice == "Custom color":
        r = int(custom_color[1:3], 16)
        g = int(custom_color[3:5], 16)
        b = int(custom_color[5:7], 16)
        bg = Image.new("RGBA", result.size, (r, g, b, 255))
        bg.paste(result, mask=result.split()[3])
        result = bg.convert("RGB")
        fmt = "JPEG"
        ext = "jpg"
    else:
        fmt = "PNG"
        ext = "png"

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original", use_container_width=True)
    with col2:
        st.image(result, caption="Background Removed", use_container_width=True)

    # download
    buf = io.BytesIO()
    result.save(buf, format=fmt)
    st.download_button(
        f"Download (.{ext})", buf.getvalue(),
        f"no_bg.{ext}", f"image/{ext}"
    )

