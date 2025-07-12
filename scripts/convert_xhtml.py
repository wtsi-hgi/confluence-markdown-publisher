#!/usr/bin/env python3
"""
Convert Markdown to XHTML using mistune for GitHub-like rendering.
"""

import re
import sys
from pathlib import Path

import mistune


def convert_markdown_to_xhtml(markdown_content):
    """Convert Markdown to XHTML using mistune with GitHub Flavored Markdown."""

    # Remove the first heading (title) from the content
    lines = markdown_content.split("\n")
    if lines and lines[0].startswith("# "):
        # Skip the title line
        markdown_content = "\n".join(lines[1:])

    # Create a markdown parser with GitHub Flavored Markdown support
    markdown = mistune.create_markdown(escape=False, hard_wrap=True)

    # Convert to HTML
    html_content = markdown(markdown_content)

    # Post-process for Confluence compatibility
    html_content = post_process_for_confluence(html_content)

    return html_content


def escape_code_block_content(content):
    """Unescape HTML entities in code block content so CDATA shows the original characters."""
    import html

    return html.unescape(content)


def post_process_for_confluence(html_content):
    """Post-process HTML to make it more Confluence-compatible."""

    # Convert code blocks to Confluence format with proper escaping
    html_content = re.sub(
        r'<pre><code class="language-(\w+)">(.*?)</code></pre>',
        lambda m: f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{m.group(1)}</ac:parameter><ac:plain-text-body><![CDATA[{escape_code_block_content(m.group(2))}]]></ac:plain-text-body></ac:structured-macro>',
        html_content,
        flags=re.DOTALL,
    )

    # Convert simple code blocks (no language specified)
    html_content = re.sub(
        r"<pre><code>(.*?)</code></pre>",
        lambda m: f'<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[{escape_code_block_content(m.group(1))}]]></ac:plain-text-body></ac:structured-macro>',
        html_content,
        flags=re.DOTALL,
    )

    # Convert inline code blocks
    html_content = re.sub(r"<code>(.*?)</code>", r"<code>\1</code>", html_content)

    # Ensure proper XHTML structure
    html_content = ensure_xhtml_structure(html_content)

    return html_content


def ensure_xhtml_structure(html_content):
    """Ensure the HTML is valid XHTML for Confluence."""

    # Fix self-closing tags
    html_content = re.sub(r"<br>", r"<br/>", html_content)
    html_content = re.sub(r"<hr>", r"<hr/>", html_content)
    html_content = re.sub(r"<img([^>]+)>", r"<img\1/>", html_content)

    # Remove double paragraph tags
    html_content = re.sub(r"<p><p>", r"<p>", html_content)
    html_content = re.sub(r"</p></p>", r"</p>", html_content)

    # Fix list structure - remove paragraph tags inside lists
    html_content = re.sub(r"<p><li>", r"<li>", html_content)
    html_content = re.sub(r"</li></p>", r"</li>", html_content)
    html_content = re.sub(r"<p></ul>", r"</ul>", html_content)
    html_content = re.sub(r"<p></ol>", r"</ol>", html_content)

    return html_content


def main():
    """Convert the specified markdown file."""
    # Get markdown file from command line argument
    if len(sys.argv) != 2:
        print("❌ Error: MD_FILE argument is required")
        print("Usage: python scripts/convert_xhtml.py <markdown_file.md>")
        sys.exit(1)

    md_file = Path(sys.argv[1])

    if not md_file.exists():
        print(f"❌ File {md_file} not found")
        print("Usage: python scripts/convert_xhtml.py <markdown_file.md>")
        sys.exit(1)

    print(f"Converting {md_file}...")

    # Read markdown content
    with open(md_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # Convert to XHTML
    xhtml_content = convert_markdown_to_xhtml(markdown_content)

    # Write to output file
    output_dir = Path("confluence_output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"{md_file.stem}_xhtml.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xhtml_content)

    print(f"Converted to {output_file}")
    print("✅ Using mistune with GitHub Flavored Markdown rendering")


if __name__ == "__main__":
    main()
