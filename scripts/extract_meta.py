"""
Auto-extracts project metadata from folder name, docstrings, and imports.
No meta.json needed — everything is derived from the code itself.
"""

import os
import re


# maps import names to human-readable tags
IMPORT_TAG_MAP = {
    "cv2": "opencv",
    "numpy": "numpy",
    "streamlit": "streamlit",
    "gradio": "gradio",
    "mediapipe": "mediapipe",
    "tensorflow": "tensorflow",
    "torch": "pytorch",
    "sklearn": "scikit-learn",
    "PIL": "pillow",
    "pytesseract": "ocr",
    "easyocr": "ocr",
    "ultralytics": "yolo",
    "dlib": "dlib",
    "matplotlib": "matplotlib",
    "plotly": "plotly",
    "pandas": "pandas",
}


def extract_meta(folder_path):
    """
    Derive name, description, and tags from the project folder.

    - Name: folder name cleaned up (e.g. '01-face-blur' → 'Face Blur')
    - Description: first docstring in app.py
    - Tags: detected from imports
    - Thumbnail: preview.png if it exists
    """
    folder_name = os.path.basename(folder_path)

    # clean folder name into a display title
    # '01-face-blur' → 'Face Blur'
    clean_name = re.sub(r"^\d+-", "", folder_name).replace("-", " ").title()

    # extract description from first docstring
    description = ""
    app_file = os.path.join(folder_path, "app.py")
    if os.path.exists(app_file):
        with open(app_file) as f:
            content = f.read()

        # try triple-quote docstring first
        match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if not match:
            match = re.search(r"'''(.+?)'''", content, re.DOTALL)
        if match:
            description = match.group(1).strip().split("\n")[0]  # first line only

        # fallback: first comment line
        if not description:
            match = re.search(r"^#\s*(.+)$", content, re.MULTILINE)
            if match:
                description = match.group(1).strip()

    # auto-detect tags from imports
    tags = []
    if os.path.exists(app_file):
        with open(app_file) as f:
            content = f.read()
        imports = set(re.findall(r"^(?:import|from)\s+(\w+)", content, re.MULTILINE))
        for imp, tag in IMPORT_TAG_MAP.items():
            if imp in imports and tag not in tags:
                tags.append(tag)

    # check for thumbnail
    thumbnail = None
    for ext in ["png", "jpg", "gif"]:
        preview_path = os.path.join(folder_path, f"preview.{ext}")
        if os.path.exists(preview_path):
            thumbnail = preview_path
            break

    return {
        "name": clean_name,
        "slug": folder_name,
        "description": description,
        "tags": tags,
        "thumbnail": thumbnail,
    }
