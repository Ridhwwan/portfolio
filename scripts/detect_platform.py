"""
Scans a project's app.py and determines which platform to deploy on.
Returns: "streamlit", "gradio", or "pyscript"
"""

import os
import re


# libraries that require a server (can't run in browser)
HEAVY_LIBS = {
    "cv2", "tensorflow", "torch", "sklearn", "mediapipe",
    "ultralytics", "scipy", "pandas", "plotly", "bokeh",
    "dlib", "keras", "transformers", "diffusers", "onnxruntime",
    "pytesseract", "easyocr", "PIL", "skimage",
}


def get_imports(filepath):
    """Extract all top-level import names from a Python file."""
    with open(filepath) as f:
        content = f.read()
    # match 'import X' and 'from X import ...'
    return set(re.findall(r"^(?:import|from)\s+(\w+)", content, re.MULTILINE))


def detect_platform(folder_path):
    """
    Decide where to deploy based on what the project imports.
    Priority: explicit framework > heavy libs needing server > lightweight browser
    """
    app_file = os.path.join(folder_path, "app.py")
    if not os.path.exists(app_file):
        return None

    imports = get_imports(app_file)

    # if the dev explicitly chose a framework, respect that
    if "streamlit" in imports:
        return "streamlit"
    if "gradio" in imports:
        return "gradio"

    # heavy libs need a real server
    if imports & HEAVY_LIBS:
        return "streamlit"

    # everything else is lightweight enough for the browser
    return "pyscript"
