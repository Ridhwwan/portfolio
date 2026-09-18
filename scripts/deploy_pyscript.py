"""
PyScript deployment handler.
Wraps the Python code in an HTML file and writes it to docs/ for GitHub Pages.
No server needed — runs entirely in the browser via WebAssembly.
"""

import os


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.8.2/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.8.2/core.js"></script>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            background: #0a0a0a;
            color: #e0e0e0;
        }}
        h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .description {{
            color: #888;
            margin-bottom: 2rem;
        }}
        #output {{
            background: #111;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 20px;
            min-height: 200px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="description">{description}</p>
    <section id="output"></section>
    <script type="py">
{code}
    </script>
</body>
</html>"""


def deploy(folder_name, title="", description=""):
    """
    Generate an HTML file wrapping the Python code in PyScript,
    write it to docs/{folder_name}/index.html for GitHub Pages.
    """
    github_user = os.environ.get("GITHUB_USER", "YOUR_USER")
    github_repo = os.environ.get("GITHUB_REPO", "python-portfolio")

    folder_path = os.path.join("projects", folder_name)
    app_file = os.path.join(folder_path, "app.py")

    with open(app_file) as f:
        code = f.read()

    # indent code to sit inside the script tag
    indented_code = "\n".join("        " + line if line.strip() else "" for line in code.split("\n"))

    html = HTML_TEMPLATE.format(
        title=title or folder_name.replace("-", " ").title(),
        description=description or "",
        code=code,
    )

    # write to docs/ for GitHub Pages
    pages_dir = os.path.join("docs", folder_name)
    os.makedirs(pages_dir, exist_ok=True)

    output_path = os.path.join(pages_dir, "index.html")
    with open(output_path, "w") as f:
        f.write(html)

    url = f"https://{github_user}.github.io/{github_repo}/{folder_name}/"
    print(f"  → PyScript: {url}")
    print(f"    Generated: {output_path}")

    return url
