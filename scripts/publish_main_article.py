#!/usr/bin/env python3
"""
Publish the main article XHTML to Confluence as a draft.
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


def create_confluence_draft(
    confluence_url, api_token, space_key, title, content, parent_page_id=None
):
    """Create a new Confluence page as draft, optionally as a subpage."""
    url = f"{confluence_url}/rest/api/content"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    data = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "status": "draft",  # Create as draft
        "body": {"storage": {"value": content, "representation": "storage"}},
    }

    # Add parent page information if specified
    if parent_page_id:
        data["ancestors"] = [{"id": parent_page_id}]
        print(f"📄 Creating as subpage under parent page ID: {parent_page_id}")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(f"✅ Successfully created draft page: {title}")
        return response.json()
    else:
        print(f"❌ Error creating page: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def get_page_id_by_title(confluence_url, api_token, space_key, page_title):
    """Get page ID by searching for a page with the given title in the space."""
    url = f"{confluence_url}/rest/api/content"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    params = {
        "spaceKey": space_key,
        "title": page_title,
        "type": "page",
        "expand": "version",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json()["results"]
        if results:
            return results[0]["id"]

    return None


def main():
    """Main function to publish the main article."""
    # Load environment variables from .env file
    load_dotenv()

    # Get markdown file from command line argument
    if len(sys.argv) != 2:
        print("❌ Error: MD_FILE argument is required")
        print("Usage: python scripts/publish_main_article.py <markdown_file.md>")
        sys.exit(1)

    md_file = Path(sys.argv[1])

    # Get environment variables
    confluence_url = os.getenv("CONFLUENCE_URL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    space_key = os.getenv("CONFLUENCE_SPACE_KEY")
    parent_page_title = os.getenv(
        "CONFLUENCE_PARENT_PAGE_TITLE"
    )  # Optional parent page title

    # Validate required environment variables
    if not all([confluence_url, api_token, space_key]):
        print("❌ Missing required environment variables")
        print("Please set: CONFLUENCE_URL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY")
        print("Make sure your .env file exists and contains these variables.")
        sys.exit(1)

    # Read the converted XHTML content
    content_file = Path(f"confluence_output/{md_file.stem}_xhtml.txt")
    if not content_file.exists():
        print(f"❌ Converted XHTML file not found: {content_file}")
        print(f"Run 'make convert MD_FILE={md_file}' first.")
        sys.exit(1)

    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Set title based on markdown file name
    title = f"{md_file.stem.replace('-', ' ').title()} (Draft)"

    print("📝 Publishing article as draft...")
    print(f"Title: {title}")
    print(f"Space: {space_key}")
    print(f"URL: {confluence_url}")

    # Handle parent page if specified
    parent_page_id = None
    if parent_page_title:
        print(f"🔍 Looking for parent page: {parent_page_title}")
        parent_page_id = get_page_id_by_title(
            confluence_url, api_token, space_key, parent_page_title
        )
        if parent_page_id:
            print(f"✅ Found parent page ID: {parent_page_id}")
        else:
            print(
                f"❌ Parent page '{parent_page_title}' not found in space '{space_key}'"
            )
            print("Creating as top-level page instead...")

    # Create the draft
    result = create_confluence_draft(
        confluence_url, api_token, space_key, title, content, parent_page_id
    )

    if result:
        page_id = result["id"]
        page_url = f"{confluence_url}/pages/viewpage.action?pageId={page_id}"
        print("\n🎉 Draft created successfully!")
        print(f"Page ID: {page_id}")
        print(f"Page URL: {page_url}")
        print("\nYou can now review and publish the draft in Confluence.")


if __name__ == "__main__":
    main()
