import os
from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator
from neuronest.core.snippet_engine import extract_smart_snippets
from neuronest.core.search_engine import SemanticIndex

def register(mcp: FastMCP, validator: VaultValidator):
    
    semantic_index = SemanticIndex(validator)
    
    @mcp.tool()
    def search_notes(query: str, snippet_mode: bool = True, max_results: int = 5, token_budget: int = 4000) -> str:
        """
        Searches all markdown notes in the configuration for the given query.
        Uses hybrid search (keyword + semantic similarity).
        """
        semantic_index.update_index()
        
        if semantic_index.model is not False:
            matches = semantic_index.search(query, top_k=max_results)
        else:
            matches = []
            for vault_name, vault_root in validator.get_all_vaults():
                for root, dirs, files in os.walk(vault_root):
                    for file in files:
                        if file.lower().endswith(('.md', '.markdown', '.txt')):
                            filepath = os.path.join(root, file)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    if query.lower() in f.read().lower():
                                        rel_path = os.path.relpath(filepath, vault_root)
                                        display_path = f"{vault_name}:{rel_path}" if len(validator.vaults) > 1 else rel_path
                                        matches.append(display_path)
                                        if len(matches) >= max_results:
                                            break
                            except Exception:
                                pass
                    if len(matches) >= max_results:
                        break
                if len(matches) >= max_results:
                    break
        
        results = []
        for display_path in matches:
            filepath = validator.validate_path(display_path, ensure_exists=True)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if snippet_mode:
                        snippet = extract_smart_snippets(content, query)
                        if not snippet:
                            snippet = content[:500] + "...\n> (Semantic match only, exact keywords not found)"
                        results.append(f"File: [{display_path}]\nSnippet:\n{snippet}")
                    else:
                        results.append(f"File: [{display_path}]\nMatch found.")
            except Exception as e:
                print(f"Error reading {display_path}: {e}")
                
        if not results:
            return f"No results found for '{query}'."
            
        response_text = "Search Results:\n\n" + "\n\n---\n\n".join(results)
        
        if token_budget and token_budget > 0:
            from neuronest.core.token_estimator import TokenEstimator
            estimator = TokenEstimator()
            response_text = estimator.trim_to_budget(response_text, token_budget)
            
        return response_text
