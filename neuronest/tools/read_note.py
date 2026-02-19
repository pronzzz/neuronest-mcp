from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator
from neuronest.utils.markdown_parser import parse_markdown_blocks
from neuronest.core.token_estimator import TokenEstimator

def register(mcp: FastMCP, validator: VaultValidator):
    
    estimator = TokenEstimator()
    
    @mcp.tool()
    def read_note(filename: str, heading_filter: str = None, token_cap: int = 4000) -> str:
        """
        Reads a markdown note from the user's vault.
        filename: relative path to the markdown file (e.g., 'ideas/project.md')
        heading_filter: return only this heading's content
        token_cap: limit the returned tokens (default 4000)
        """
        filepath = validator.validate_path(filename, ensure_exists=True)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if heading_filter:
            blocks = parse_markdown_blocks(content)
            filtered_blocks = []
            for b in blocks:
                if b.headings and heading_filter.lower() in [h.lower() for h in b.headings]:
                    filtered_blocks.append(b.content)
            if filtered_blocks:
                content = "\n\n".join(filtered_blocks)
            else:
                return f"Heading '{heading_filter}' not found in {filename}."
                
        if token_cap and token_cap > 0:
            content = estimator.trim_to_budget(content, token_cap)
            
        return content
