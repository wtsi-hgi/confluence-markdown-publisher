# Confluence Markdown Publisher

1. **Find your Confluence API token** ([instructions](https://confluence.sanger.ac.uk/plugins/personalaccesstokens/usertokens.action)).
2. **Publish a Markdown file that is put in docs/:**

```bash
make all MD_FILE=your-file.md
```

- The first time you run, you'll be prompted for your Confluence URL, space key, and API token.
- The tool will automatically set up everything else (dependencies, environment, etc).
- Your Markdown file must be in the `docs/` directory.
- To see available files:

```bash
make list
``` 