"""Upload any image and extract its dominant color palette using K-Means clustering."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def extract_palette(image, n_colors=5):
    """Use K-Means clustering to find the dominant colors in an image."""
    # reshape image to be a list of pixels
    pixels = image.reshape(-1, 3).astype(np.float32)

    # run k-means
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # get colors and their proportions
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    counts = np.bincount(labels)
    percentages = counts / len(labels)

    # sort by frequency (most dominant first)
    order = np.argsort(-percentages)
    colors = colors[order]
    percentages = percentages[order]

    return colors, percentages


def draw_palette(colors, percentages, width=600, height=80):
    """Draw a horizontal palette bar showing each color proportionally."""
    palette = np.zeros((height, width, 3), dtype=np.uint8)
    x_start = 0
    for color, pct in zip(colors, percentages):
        x_end = x_start + int(width * pct)
        palette[:, x_start:x_end] = color
        x_start = x_end
    return palette


st.set_page_config(page_title="Color Palette Extractor", layout="centered")
st.title("Color Palette Extractor")
st.write("Upload an image and extract its dominant colors.")

n_colors = st.slider("Number of colors to extract", 3, 10, 5)

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = np.array(Image.open(uploaded))

    # resize for faster processing
    h, w = img.shape[:2]
    if max(h, w) > 600:
        scale = 600 / max(h, w)
        img_small = cv2.resize(img, (int(w * scale), int(h * scale)))
    else:
        img_small = img

    with st.spinner("Extracting colors..."):
        colors_rgb, percentages = extract_palette(img_small, n_colors)

    # display original image
    st.image(img, caption="Original", use_container_width=True)

    # draw and display palette
    palette_img = draw_palette(colors_rgb, percentages)
    st.image(palette_img, caption="Dominant Colors", use_container_width=True)

    # show individual colors with hex codes
    cols = st.columns(n_colors)
    for i, (color, pct) in enumerate(zip(colors_rgb, percentages)):
        hex_code = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
        with cols[i]:
            swatch = np.full((60, 60, 3), color, dtype=np.uint8)
            st.image(swatch, use_container_width=True)
            st.caption(f"{hex_code}\n{pct:.0%}")
