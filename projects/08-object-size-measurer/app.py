"""Measure real-world sizes of objects in a photo using a reference object (like a coin or card)."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image


def find_objects(image, min_area=1000):
    """Find object contours in the image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blurred, 30, 100)
    dilated = cv2.dilate(edged, None, iterations=2)
    eroded = cv2.erode(dilated, None, iterations=1)

    contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # filter by area and sort left-to-right
    contours = [c for c in contours if cv2.contourArea(c) > min_area]
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
    return contours


def get_dimensions(contour, pixels_per_cm):
    """Get width and height of a contour in centimeters."""
    rect = cv2.minAreaRect(contour)
    (_, (w, h), _) = rect
    width_cm = w / pixels_per_cm
    height_cm = h / pixels_per_cm
    return width_cm, height_cm, rect


st.set_page_config(page_title="Object Size Measurer", layout="centered")
st.title("Object Size Measurer")
st.write(
    "Upload a top-down photo with multiple objects. "
    "The leftmost object is used as the size reference."
)

ref_width_cm = st.number_input(
    "Width of the reference object (cm)",
    min_value=0.1, max_value=100.0, value=2.5, step=0.1,
    help="The real-world width of the leftmost object in the photo (e.g., a coin = 2.5 cm)"
)

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = np.array(Image.open(uploaded))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    contours = find_objects(img_bgr)

    if len(contours) < 2:
        st.warning("Need at least 2 objects — one reference and one to measure.")
        st.image(img, use_container_width=True)
    else:
        # use leftmost contour as reference
        ref_contour = contours[0]
        ref_rect = cv2.minAreaRect(ref_contour)
        ref_width_px = max(ref_rect[1])  # larger dimension in pixels

        pixels_per_cm = ref_width_px / ref_width_cm

        # annotate all objects
        annotated = img.copy()
        for i, c in enumerate(contours):
            w_cm, h_cm, rect = get_dimensions(c, pixels_per_cm)

            box = cv2.boxPoints(rect).astype(int)
            color = (0, 255, 0) if i == 0 else (255, 100, 0)
            label = "REF" if i == 0 else f"{max(w_cm, h_cm):.1f} x {min(w_cm, h_cm):.1f} cm"

            cv2.drawContours(annotated, [box], 0, color, 2)

            # put label above the box
            cx, cy = int(rect[0][0]), int(rect[0][1]) - 15
            cv2.putText(annotated, label, (cx - 40, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        st.image(annotated, caption="Measured Objects", use_container_width=True)
        st.caption(f"Scale: {pixels_per_cm:.1f} pixels/cm (based on reference = {ref_width_cm} cm)")

