"""
Streamlit deployment handler.

Streamlit Cloud auto-deploys from GitHub when connected, so this script
just returns the expected URL. You connect each project once in the
Streamlit Cloud dashboard — after that, pushes auto-deploy.

URL pattern: https://{repo-name}-{folder-name}.streamlit.app
(Streamlit generates this based on your repo and file path)
"""

import os


def deploy(folder_name):
    """
    Return the Streamlit Cloud URL for this project.
    Streamlit auto-deploys from GitHub, so no action needed here.
    """
    github_user = os.environ.get("GITHUB_USER", "YOUR_USER")
    github_repo = os.environ.get("GITHUB_REPO", "python-portfolio")

    # Streamlit Cloud URL pattern — adjust if yours differs
    url = f"https://{github_repo}-{folder_name}.streamlit.app"

    print(f"  → Streamlit: {url}")
    print(f"    (Make sure this project is connected in Streamlit Cloud)")
    print(f"    App path: projects/{folder_name}/app.py")

    return url
