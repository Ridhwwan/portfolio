"""Upload a photo of a hand and count the number of raised fingers using MediaPipe."""

import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image


def count_fingers(hand_landmarks):
    """Count raised fingers based on landmark positions."""
    tips = [
        mp.solutions.hands.HandLandmark.THUMB_TIP,
        mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
        mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp.solutions.hands.HandLandmark.RING_FINGER_TIP,
        mp.solutions.hands.HandLandmark.PINKY_TIP,
    ]
    pips = [
        mp.solutions.hands.HandLandmark.THUMB_IP,
        mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP,
        mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp.solutions.hands.HandLandmark.RING_FINGER_PIP,
        mp.solutions.hands.HandLandmark.PINKY_PIP,
    ]

    count = 0
    landmarks = hand_landmarks.landmark

    # thumb — compare x position (works for right hand facing camera)
    if abs(landmarks[tips[0]].x - landmarks[pips[0]].x) > 0.05:
        count += 1

    # other fingers — tip above pip means extended
    for i in range(1, 5):
        if landmarks[tips[i]].y < landmarks[pips[i]].y:
            count += 1

    return count


st.set_page_config(page_title="Finger Counter", layout="centered")
st.title("Hand Gesture — Finger Counter")
st.write("Upload a photo showing your hand. MediaPipe detects the hand and counts raised fingers.")

uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded:
    img = np.array(Image.open(uploaded))

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5
    ) as hands:
        results = hands.process(img)

    if results.multi_hand_landmarks:
        annotated = img.copy()
        total_fingers = 0

        for hand_lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(annotated, hand_lm, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(hand_lm)
            total_fingers += fingers

        st.image(annotated, caption=f"Detected {total_fingers} finger(s) up", use_container_width=True)
        st.metric("Fingers Raised", total_fingers)
    else:
        st.warning("No hand detected. Try a clearer photo with your hand visible.")
        st.image(img, use_container_width=True)
