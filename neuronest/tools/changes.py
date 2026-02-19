import os
import datetime
from pathlib import Path
from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator
from neuronest.utils.markdown_parser import parse_markdown_blocks

def register(mcp: FastMCP, validator: VaultValidator):
    
    @mcp.tool()
    def recent_changes(hours: int = 24) -> str:
        """
        Returns a list of files modified in the last `hours` hours across all configured vaults,
        extracting the most recently modified sections (or the end of the file/highlights).
        """
        now = datetime.datetime.now()
        threshold = now - datetime.timedelta(hours=hours)
        
        modified_files = []
        for vault_name, vault_root in validator.get_all_vaults():
            for root, dirs, files in os.walk(vault_root):
                if '.git' in root or '.obsidian' in root or '.neuronest' in root:
                    continue
                for file in files:
                    if file.lower().endswith(('.md', '.markdown', '.txt')):
                        filepath = Path(root) / file
                        try:
                            mtime = datetime.datetime.fromtimestamp(filepath.stat().st_mtime)
                            if mtime >= threshold:
                                modified_files.append((filepath, mtime, vault_name))
                        except Exception:
                            pass
                        
        if not modified_files:
            return f"No notes modified in the last {hours} hours."
            
        modified_files.sort(key=lambda x: x[1], reverse=True)
        
        results = [f"# Changes in the last {hours} hours\n"]
        
        for filepath, mtime, vault_name in modified_files[:10]: # Cap to top 10 most recent to save tokens
            rel_path = validator.to_relative(filepath)
            display_path = rel_path if vault_name == "default" and len(validator.vaults) == 1 else f"{vault_name}:{rel_path}"
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                blocks = parse_markdown_blocks(content)
                target_blocks = blocks[-3:] if len(blocks) >= 3 else blocks
                snippet = "\n\n".join(b.content for b in target_blocks)
                
                results.append(f"## {display_path} (Modified: {mtime.strftime('%Y-%m-%d %H:%M')})")
                results.append(f"Most recent sections:\n{snippet}\n")
            except Exception:
                pass
                
        if len(modified_files) > 10:
            results.append(f"... and {len(modified_files) - 10} more files.")
            
        return "\n".join(results)
