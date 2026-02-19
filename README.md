# NeuroNest MCP

> Your AI's private doorway into your Second Brain.

NeuroNest MCP is a robust, local-first, minimal-dependency Model Context Protocol (MCP) server that securely connects any MCP-compliant AI agent (Claude, Cursor, etc.) to your Markdown-based knowledge base (Obsidian, Logseq, or plain folders).

## Features

- **Local-First & Private:** Zero cloud dependencies, zero tracking. All processing happens on your machine.
- **Multi-Vault Support:** Connect multiple folders or Obsidian vaults simultaneously.
- **Smart Snippet Extraction:** Doesn't dump entire files into context. Intelligently extracts relevant paragraphs and preserves Markdown heading hierarchy.
- **Semantic Search:** Lightweight local embeddings (using `sentence-transformers`) for hybrid keyword + semantic search.
- **Daily Digest Protocol:** An executive assistant primitive that scans for tasks and highlights (`#idea`, `#task`, etc.) modified in the last 24 hours.
- **Knowledge Graph Extraction:** Understands `[[wikilinks]]` and `#tags` to navigate related concepts without a graph database.
- **Change Awareness:** Gives AI temporal context on what you modified recently.
- **Token Budgeting:** Actively manages LLM context window size using standard token estimation (`tiktoken`).

## Quick Start

1. Install dependencies:

   ```bash
   pip install fastmcp pydantic tiktoken sentence-transformers
   ```

2. Configure your Vault Path:
   Set the environment variable or let the server default to the current directory.

   ```bash
   export NEURONEST_VAULT_PATH="/path/to/your/obsidian/vault"
   ```

3. Run the Server:

   ```bash
   python neuronest/server.py
   ```

## Development

NeuroNest uses `fastmcp` to expose tools to Claude or Cursor. See `GUIDE.md` for a complete breakdown of tools and architecture.
