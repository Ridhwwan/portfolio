"""Upload two photos taken moments apart and detect what moved between them."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image


st.set_page_config(page_title="Motion Detector", layout="centered")
st.title("Motion Detector")
st.write("Upload two photos of the same scene taken moments apart. The app highlights what moved.")

sensitivity = st.slider("Sensitivity (lower = more sensitive)", 10, 100, 30)
min_area = st.slider("Minimum detection area (pixels)", 100, 5000, 500)

col1, col2 = st.columns(2)
with col1:
    frame1_file = st.file_uploader("Frame 1 (before)", type=["jpg", "jpeg", "png"])
with col2:
    frame2_file = st.file_uploader("Frame 2 (after)", type=["jpg", "jpeg", "png"])

if frame1_file and frame2_file:
    frame1 = np.array(Image.open(frame1_file))
    frame2 = np.array(Image.open(frame2_file))

    # ensure same size
    h, w = frame1.shape[:2]
    frame2 = cv2.resize(frame2, (w, h))

    # convert to grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)

    # blur to reduce noise
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

    # compute absolute difference
    diff = cv2.absdiff(gray1, gray2)

    # threshold the difference
    _, thresh = cv2.threshold(diff, sensitivity, 255, cv2.THRESH_BINARY)

    # dilate to fill gaps
    thresh = cv2.dilate(thresh, None, iterations=3)

    # find contours of moved regions
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # draw bounding boxes on frame2
    result = frame2.copy()
    motion_count = 0
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        (x, y, w_box, h_box) = cv2.boundingRect(c)
        cv2.rectangle(result, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
        motion_count += 1

    st.image(result, caption=f"Motion detected: {motion_count} region(s)", use_container_width=True)

    # show the raw difference map
    with st.expander("Show difference heatmap"):
        heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        st.image(heatmap_rgb, caption="Difference Heatmap", use_container_width=True)
