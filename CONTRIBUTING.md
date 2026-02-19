# Contributing to NeuroNest

Thank you for your interest! We welcome pull requests.

## Setup

1. Clone the repo.
2. We recommend `uv` for lightning-fast dependency resolution:

   ```bash
   uv venv
   uv pip install -e .
   ```

3. Test the server locally:

   ```bash
   python neuronest/server.py
   ```

## Guidelines

- **Token Efficiency:** Any new tool must respect context window sizes. When in doubt, chunk output.
- **Privacy:** Do not introduce telemetry, external un-prompted network calls, or analytics.
- **Dependency Minimization:** FastMCP/Pydantic/TikToken/Sentence-Transformers are the core. Avoid new heavy dependencies unless strictly necessary.

Please open an issue to discuss major architectural changes before submitting a PR.
