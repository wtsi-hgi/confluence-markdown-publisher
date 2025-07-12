# Makefile for Local Confluence Publishing

.PHONY: help convert publish clean all list deps setup ensure-env ensure-uv ensure-venv

MD_FILES := $(wildcard docs/*.md)

PYTHON := $(shell which python3)

help:
	@echo "Available targets:"
	@echo "  list     - List all available markdown files"
	@echo "  convert  - Convert Markdown to XHTML for Confluence"
	@echo "  publish  - Publish article as draft to Confluence"
	@echo "  clean    - Remove generated files"
	@echo "  all      - Convert and publish (complete process)"
	@echo "  deps     - Install dependencies"
	@echo "  setup    - Initial project setup"
	@echo ""
	@echo "Usage:"
	@echo "  make list"
	@echo "  make convert MD_FILE=your-file.md"
	@echo "  make publish MD_FILE=your-file.md"
	@echo "  make all MD_FILE=your-file.md"
	@echo ""
	@echo "Note: MD_FILE argument is required for convert, publish, and all targets"
	@echo "      Files are automatically looked for in the docs/ directory"

list:
	@echo "📚 Available markdown files in docs/:"
	@for file in $(MD_FILES); do \
		echo "  $$(basename $$file)"; \
	done
	@echo ""
	@echo "Use: make all MD_FILE=filename.md"

ensure-env:
	@if [ ! -f .env ]; then \
		echo "No .env found. Let's set up your Confluence credentials."; \
		echo -n 'Confluence URL (press Enter for default: https://confluence.sanger.ac.uk): '; \
		read url; \
		if [ -z "$$url" ]; then url="https://confluence.sanger.ac.uk"; fi; \
		echo -n 'Confluence Space Key (press Enter for default: HGI): '; \
		read space; \
		if [ -z "$$space" ]; then space="HGI"; fi; \
		token=""; \
		while [ -z "$$token" ]; do \
			echo -n 'Confluence API Token (required): '; \
			read token; \
		done; \
		echo -n 'Confluence Parent Page Title (press Enter for default: HGI Home): '; \
		read parent; \
		if [ -z "$$parent" ]; then parent="HGI Home"; fi; \
		echo "CONFLUENCE_URL=$$url" > .env; \
		echo "CONFLUENCE_SPACE_KEY=$$space" >> .env; \
		echo "CONFLUENCE_API_TOKEN=$$token" >> .env; \
		echo "CONFLUENCE_PARENT_PAGE_TITLE=$$parent" >> .env; \
		echo ".env created."; \
	fi

ensure-uv:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "uv not found, installing with pip..."; \
		$(PYTHON) -m pip install --user uv; \
		echo "Adding uv to PATH..."; \
		export PATH="$$HOME/.local/bin:$$PATH"; \
	fi

ensure-venv:
	@if [ ! -d .venv ]; then \
		echo "Creating virtual environment..."; \
		uv venv; \
		echo "Installing dependencies..."; \
		uv sync; \
	fi

deps: ensure-uv ensure-venv
	@echo "✅ Dependencies installed"

convert: ensure-env ensure-uv ensure-venv
	@if [ -z "$(MD_FILE)" ]; then \
		echo "❌ Error: MD_FILE argument is required"; \
		echo "Usage: make convert MD_FILE=your-file.md"; \
		exit 1; \
	fi
	@if [ ! -f "docs/$(MD_FILE)" ] && [ ! -f "$(MD_FILE)" ]; then \
		echo "❌ Error: File docs/$(MD_FILE) not found"; \
		echo "Available files:"; \
		for file in docs/*.md; do \
			echo "  $$(basename $$file)"; \
		done; \
		exit 1; \
	fi
	@if [ -f "docs/$(MD_FILE)" ]; then \
		echo "🔄 Converting docs/$(MD_FILE) to XHTML..."; \
		.venv/bin/python scripts/convert_xhtml.py docs/$(MD_FILE); \
	else \
		echo "🔄 Converting $(MD_FILE) to XHTML..."; \
		.venv/bin/python scripts/convert_xhtml.py $(MD_FILE); \
	fi
	@echo "✅ Conversion complete"

publish: ensure-env ensure-uv ensure-venv
	@if [ -z "$(MD_FILE)" ]; then \
		echo "❌ Error: MD_FILE argument is required"; \
		echo "Usage: make publish MD_FILE=your-file.md"; \
		exit 1; \
	fi
	@if [ ! -f "docs/$(MD_FILE)" ] && [ ! -f "$(MD_FILE)" ]; then \
		echo "❌ Error: File docs/$(MD_FILE) not found"; \
		echo "Available files:"; \
		for file in docs/*.md; do \
			echo "  $$(basename $$file)"; \
		done; \
		exit 1; \
	fi
	@if [ -f "docs/$(MD_FILE)" ]; then \
		echo "📝 Publishing docs/$(MD_FILE) to Confluence..."; \
		.venv/bin/python scripts/publish_main_article.py docs/$(MD_FILE); \
	else \
		echo "📝 Publishing $(MD_FILE) to Confluence..."; \
		.venv/bin/python scripts/publish_main_article.py $(MD_FILE); \
	fi
	@echo "✅ Publication complete"

all: ensure-env ensure-uv ensure-venv convert publish

clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf confluence_output/
	@echo "✅ Clean complete"

setup: deps
	@echo "🚀 Project setup complete!"
	@echo "Run 'make list' to see available markdown files"
	@echo "Run 'make convert' to convert your Markdown files"
	@echo "Run 'make publish' to publish to Confluence (requires env vars)" 

 