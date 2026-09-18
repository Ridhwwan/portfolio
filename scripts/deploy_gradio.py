"""
Gradio deployment handler.
Pushes the project folder to a HuggingFace Space for hosting.
Requires HF_TOKEN in environment.
"""

import os
import subprocess


def deploy(folder_name):
    """
    Upload the project to a HuggingFace Space.
    Creates the Space if it doesn't exist.
    """
    github_user = os.environ.get("GITHUB_USER", "YOUR_USER")
    hf_token = os.environ.get("HF_TOKEN", "")
    space_name = f"{github_user}/{folder_name}"
    folder_path = os.path.join("projects", folder_name)

    if not hf_token:
        print(f"  ⚠ HF_TOKEN not set — skipping HuggingFace deploy for {folder_name}")
        return f"https://huggingface.co/spaces/{space_name}"

    # create the space if it doesn't exist
    try:
        subprocess.run(
            [
                "huggingface-cli", "repo", "create",
                folder_name,
                "--type", "space",
                "--space_sdk", "gradio",
            ],
            check=False,  # don't fail if already exists
            capture_output=True,
        )
    except FileNotFoundError:
        print("  ⚠ huggingface-cli not found — install with: pip install huggingface_hub")
        return f"https://huggingface.co/spaces/{space_name}"

    # upload folder contents
    subprocess.run(
        [
            "huggingface-cli", "upload", space_name,
            folder_path, ".",
            "--repo-type", "space",
        ],
        check=True,
    )

    url = f"https://huggingface.co/spaces/{space_name}"
    print(f"  → Gradio: {url}")
    return url
