"""
Main orchestrator — called by GitHub Actions on every push.
For each changed project folder:
  1. Detects the right platform
  2. Extracts metadata from the code
  3. Deploys to the appropriate service
  4. Syncs the entry to Notion
"""

import sys
import os

# add scripts dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detect_platform import detect_platform
from extract_meta import extract_meta
from sync_to_notion import (
    get_notion_client,
    get_database_id,
    get_existing_entries,
    sync_project,
)
import deploy_streamlit
import deploy_gradio
import deploy_pyscript


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("No changed folders provided. Nothing to deploy.")
        return

    changed_folders = sys.argv[1].strip().split()
    print(f"\n{'='*50}")
    print(f"Deploying {len(changed_folders)} project(s)")
    print(f"{'='*50}\n")

    # connect to Notion once
    notion = get_notion_client()
    db_id = get_database_id()
    existing_entries = get_existing_entries(notion, db_id)
    print(f"Found {len(existing_entries)} existing entries in Notion\n")

    for folder_name in changed_folders:
        folder_path = os.path.join("projects", folder_name)

        if not os.path.isdir(folder_path):
            print(f"⚠ Skipping '{folder_name}' — not a directory")
            continue

        print(f"─── {folder_name} ───")

        # 1. detect platform
        platform = detect_platform(folder_path)
        if platform is None:
            print(f"  ⚠ No app.py found — skipping")
            continue
        print(f"  Platform: {platform}")

        # 2. extract metadata
        meta = extract_meta(folder_path)
        print(f"  Name: {meta['name']}")
        print(f"  Tags: {meta['tags']}")

        # 3. deploy to the right service
        if platform == "streamlit":
            url = deploy_streamlit.deploy(folder_name)
        elif platform == "gradio":
            url = deploy_gradio.deploy(folder_name)
        elif platform == "pyscript":
            url = deploy_pyscript.deploy(
                folder_name,
                title=meta["name"],
                description=meta["description"],
            )
        else:
            print(f"  ⚠ Unknown platform '{platform}' — skipping")
            continue

        # 4. sync to Notion
        sync_project(
            name=meta["name"],
            description=meta["description"],
            url=url,
            platform=platform,
            tags=meta["tags"],
            existing_entries=existing_entries,
            notion=notion,
            db_id=db_id,
        )

        # track the name so subsequent runs know it exists
        existing_entries[meta["name"]] = "synced"

        print()

    print(f"{'='*50}")
    print("Done.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
