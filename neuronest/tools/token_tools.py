from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator
from neuronest.core.token_estimator import TokenEstimator

def register(mcp: FastMCP, validator: VaultValidator):
    
    estimator = TokenEstimator()
    
    @mcp.tool()
    def estimate_token_size(text: str) -> str:
        """
        Estimates the number of tokens in the given text using standard LLM tokenization (tiktoken cl100k_base).
        """
        count = estimator.count_tokens(text)
        return f"Token count: {count}"
