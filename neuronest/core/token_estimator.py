import tiktoken

class TokenEstimator:
    def __init__(self, model_name: str = "gpt-4o"):
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
        
    def trim_to_budget(self, text: str, max_tokens: int) -> str:
        """Trims text to fit within max_tokens, appending an indicator if truncated."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
            
        # Leave a few tokens for the truncation message
        truncated_tokens = tokens[:max_tokens - 10]
        truncated_text = self.encoding.decode(truncated_tokens)
        
        return truncated_text + "\n\n... [Content truncated to fit token budget]"
