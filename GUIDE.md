# NeuroNest MCP - Detailed Guide

## Architecture

NeuroNest is built on `fastmcp` for an asynchronous, minimal-boilerplate integration with the Model Context Protocol (MCP).

### Core Components

1. **Vault Validator (`core/vault_validator.py`)**
   - Ensures no directory traversal attacks occur (`../../etc/passwd`).
   - Resolves all paths explicitly to the specified Vault Roots.
   - Restricts operations to `.md`, `.txt`, `.markdown` extensions.

2. **Snippet Engine (`core/snippet_engine.py`)**
   - Parses Markdown blocks dynamically.
   - Instead of returning entire files (which crushes LLM context windows), it returns only paragraphs containing the semantic matches, plus contextual surrounding blocks and heading hierarchy.

3. **Semantic Index (`core/search_engine.py`)**
   - Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to create local, privacy-preserving embeddings.
   - Caches embeddings in `.neuronest_index.json` at the root of your vault.
   - Enables hybrid searches (exact match + semantic similarity).

4. **Token Estimator (`core/token_estimator.py`)**
   - Uses `tiktoken` to count response sizes.
   - Truncates excessively large returns before they hit the MCP transport layer.

## Tools Exposed

### `read_note(filename, heading_filter=None, token_cap=4000)`

Directly fetches the content of a file. Optionally filters by a specific heading hierarchy.

### `search_notes(query, snippet_mode=True, max_results=5, token_budget=4000)`

Performs a hybrid search across all loaded vaults. Returns highly-relevant contextual snippets rather than raw dumped files.

### `append_to_daily_note(text)`

Auto-creates (if missing) and appends a timestamped bullet to `Daily/YYYY-MM-DD.md` in the default vault.

### `daily_briefing()`

Scans the vault for any file modified in the last 24 hours. Extracts uncompleted tasks (`- [ ]`) and key tags (`#idea`, `#task`, `#meeting`) into an executive summary.

### `recent_changes(hours=24)`

Returns the actual file diffs/snippets of notes modified within the given time threshold, giving LLMs temporal awareness.

### `get_backlinks(note_name)`

Finds all files containing `[[wikilinks]]` pointing to the specified note.

### `get_related_notes(note_name)`

Calculates note similarity based on shared `#tags` and explicit outbound links.

### `estimate_token_size(text)`

Utility tool for agents to check how much context a string will consume.
