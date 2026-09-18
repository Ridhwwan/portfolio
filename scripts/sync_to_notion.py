"""
Syncs project metadata to a Notion database.
- New project folder → creates a new entry
- Existing project folder → updates the entry (bumps 'Last edited time')
- Sort Order is left untouched so manual pinning is preserved
"""

import os
from notion_client import Client


def get_notion_client():
    return Client(auth=os.environ["NOTION_TOKEN"])


def get_database_id():
    return os.environ["NOTION_DB_ID"]


def get_existing_entries(notion, db_id):
    """Fetch all entries from the Notion database, keyed by project name."""
    existing = {}
    has_more = True
    start_cursor = None

    while has_more:
        kwargs = {"database_id": db_id}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        response = notion.databases.query(**kwargs)
        for page in response["results"]:
            title_prop = page["properties"].get("Name", {}).get("title", [])
            if title_prop:
                name = title_prop[0]["plain_text"]
                existing[name] = page["id"]

        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

    return existing


def sync_project(name, description, url, platform, tags, existing_entries, notion, db_id):
    """Create or update a single project entry in Notion."""
    properties = {
        "Name": {"title": [{"text": {"content": name}}]},
        "Description": {"rich_text": [{"text": {"content": description or ""}}]},
        "URL": {"url": url},
        "Platform": {"select": {"name": platform}},
        "Tags": {"multi_select": [{"name": t} for t in tags]},
    }

    if name in existing_entries:
        # update — this bumps 'Last edited time' automatically
        page_id = existing_entries[name]
        notion.pages.update(page_id=page_id, properties=properties)
        print(f"  ✓ Updated in Notion: {name}")
    else:
        # create new entry
        notion.pages.create(
            parent={"database_id": db_id},
            properties=properties,
        )
        print(f"  ✓ Created in Notion: {name}")
