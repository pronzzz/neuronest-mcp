from neuronest.config import load_config
from neuronest.core.vault_validator import VaultValidator
from neuronest.tools import read_note, search_notes, append, daily_digest, token_tools, graph

def create_server() -> FastMCP:
    config = load_config()
    validator = VaultValidator(config.vault_path)
    
    mcp = FastMCP("NeuroNest", dependencies=["fastmcp", "pydantic", "tiktoken", "sentence-transformers"])
    
    read_note.register(mcp, validator)
    search_notes.register(mcp, validator)
    append.register(mcp, validator)
    daily_digest.register(mcp, validator)
    token_tools.register(mcp, validator)
    graph.register(mcp, validator)
    
    return mcp

def main():
    mcp = create_server()
    mcp.run()

if __name__ == "__main__":
    main()
