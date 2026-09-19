"""Upload 2-5 overlapping photos and stitch them into a single panorama."""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io


st.set_page_config(page_title="Panorama Stitcher", layout="centered")
st.title("Panorama Stitcher")
st.write(
    "Upload 2-5 overlapping photos taken from the same position. "
    "OpenCV will detect matching features and stitch them together."
)

uploaded_files = st.file_uploader(
    "Choose images (2-5, with overlap between neighbors)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
    if len(uploaded_files) < 2:
        st.warning("Upload at least 2 images.")
    elif len(uploaded_files) > 5:
        st.warning("Maximum 5 images for performance. Upload fewer images.")
    else:
        images = []
        cols = st.columns(len(uploaded_files))
        for i, f in enumerate(uploaded_files):
            img = np.array(Image.open(f))
            # resize for faster processing
            h, w = img.shape[:2]
            if max(h, w) > 800:
                scale = 800 / max(h, w)
                img = cv2.resize(img, (int(w * scale), int(h * scale)))
            images.append(img)
            with cols[i]:
                st.image(img, caption=f"Image {i+1}", use_container_width=True)

        with st.spinner("Stitching... (detecting features and aligning images)"):
            # OpenCV's built-in stitcher handles feature detection,
            # matching, homography, and blending automatically
            stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)

            # convert RGB to BGR for OpenCV
            bgr_images = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in images]
            status, pano = stitcher.stitch(bgr_images)

        if status == cv2.Stitcher_OK:
            result = cv2.cvtColor(pano, cv2.COLOR_BGR2RGB)
            st.image(result, caption="Stitched Panorama", use_container_width=True)

            # download
            result_pil = Image.fromarray(result)
            buf = io.BytesIO()
            result_pil.save(buf, format="JPEG", quality=90)
            st.download_button(
                "Download panorama",
                buf.getvalue(),
                "panorama.jpg",
                "image/jpeg"
            )
        elif status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
            st.error("Not enough overlap between images. Try photos with more shared content.")
        elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
            st.error("Could not align images. Make sure they overlap and are from the same viewpoint.")
        else:
            st.error("Stitching failed. Try different images with more overlap.")

