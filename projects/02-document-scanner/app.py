"""Take a photo of a document and get a clean, flat, cropped scan."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image


def order_points(pts):
    """Sort 4 points into: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]      # top-left has smallest sum
    rect[2] = pts[np.argmax(s)]      # bottom-right has largest sum
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]   # top-right has smallest difference
    rect[3] = pts[np.argmax(diff)]   # bottom-left has largest difference
    return rect


def four_point_transform(image, pts):
    """Warp perspective to get a top-down view of the document."""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width and height of the new image
    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, matrix, (max_width, max_height))


st.set_page_config(page_title="Document Scanner", layout="centered")
st.title("Document Scanner")
st.write("Upload a photo of a document — edges will be detected and the document straightened.")

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = np.array(Image.open(uploaded))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    orig = img_bgr.copy()

    # resize for processing
    ratio = img_bgr.shape[0] / 500.0
    resized = cv2.resize(img_bgr, (int(img_bgr.shape[1] / ratio), 500))

    # edge detection pipeline
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)

    # find contours — the document should be the largest 4-sided contour
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    doc_contour = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_contour = approx
            break

    if doc_contour is not None:
        # scale contour back to original image size
        doc_contour = doc_contour.reshape(4, 2) * ratio

        # apply perspective transform
        scanned = four_point_transform(orig, doc_contour)
        scanned_gray = cv2.cvtColor(scanned, cv2.COLOR_BGR2GRAY)
        scanned_clean = cv2.adaptiveThreshold(
            scanned_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Original", use_container_width=True)
        with col2:
            st.image(scanned_clean, caption="Scanned", use_container_width=True)
    else:
        st.warning("Could not detect document edges. Try a photo with more contrast between the document and background.")
        st.image(img, caption="Original", use_container_width=True)
