# Python Portfolio — Auto-Deploy Pipeline

A self-updating portfolio that detects your Python projects, deploys them to the right platform, syncs metadata to Notion, and displays them on your Framer site.

## How It Works

1. **You** create a folder in `projects/` and write your `app.py`
2. **GitHub Actions** detects the commit, scans imports, and picks a platform:
   - Heavy libraries (OpenCV, TensorFlow, MediaPipe) → **Streamlit Cloud**
   - Gradio imports → **HuggingFace Spaces**
   - Lightweight Python only → **PyScript on GitHub Pages**
3. **Notion** gets updated automatically (new entry or updated timestamp)
4. **Framer** reads from Notion and renders the project grid

## Setup (One-Time)

### 1. Notion
- Create a database with these properties:
  - `Name` (Title)
  - `Description` (Text)
  - `URL` (URL)
  - `Platform` (Select: streamlit / gradio / pyscript)
  - `Tags` (Multi-select)
  - `Thumbnail` (Files & media)
  - `Sort Order` (Number) — leave empty for auto-sort, set a number to pin
- Create a [Notion integration](https://www.notion.so/my-integrations) and share the database with it
- Copy the integration token and database ID

### 2. GitHub Secrets
Add these to your repo → Settings → Secrets and variables → Actions:
- `NOTION_TOKEN` — your Notion integration token
- `NOTION_DB_ID` — your Notion database ID
- `HF_TOKEN` — (optional) HuggingFace token if using Gradio projects

### 3. Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io)
- Connect this GitHub repo
- Each Streamlit project needs to be added once (after that, it auto-deploys on push)

### 4. GitHub Pages
- Go to repo Settings → Pages → Source → Deploy from a branch → `main` / `docs`

### 5. Framer
- Add the code component from `framer/ProjectGrid.tsx` to your site
- Update the Notion query endpoint or use the Notion integration

## Adding a New Project

```bash
mkdir projects/my-new-project
# write your app.py
git add . && git commit -m "Add my-new-project" && git push
# done — it shows up on your site
```

## Folder Structure

```
python-portfolio/
├── .github/workflows/deploy.yml
├── scripts/
│   ├── detect_platform.py
│   ├── extract_meta.py
│   ├── deploy_all.py
│   ├── deploy_streamlit.py
│   ├── deploy_gradio.py
│   ├── deploy_pyscript.py
│   └── sync_to_notion.py
├── docs/                          ← GitHub Pages (auto-generated)
├── framer/
│   └── ProjectGrid.tsx
├── projects/
│   ├── 01-face-blur/
│   │   └── app.py
│   ├── 02-document-scanner/
│   │   └── app.py
│   └── ...
└── README.md
```
