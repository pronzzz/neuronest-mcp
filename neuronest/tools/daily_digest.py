import os
import datetime
from pathlib import Path
from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator
from neuronest.utils.markdown_parser import parse_markdown_blocks

def register(mcp: FastMCP, validator: VaultValidator):
    
    @mcp.tool()
    def daily_briefing() -> str:
        """
        Scans all configured vaults for notes modified in the last 24 hours.
        Extracts TODOs, tasks, and new headings to build an executive summary.
        """
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        
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
                            if mtime >= yesterday:
                                modified_files.append((filepath, vault_name))
                        except Exception:
                            pass
                        
        if not modified_files:
            return "No notes modified in the last 24 hours."
            
        digest = [f"# Daily Briefing for {now.strftime('%Y-%m-%d')}"]
        digest.append(f"Found {len(modified_files)} modified notes.\n")
        
        all_todos = []
        all_highlights = []
        
        for filepath, vault_name in modified_files:
            rel_path = validator.to_relative(filepath)
            display_path = rel_path if vault_name == "default" and len(validator.vaults) == 1 else f"{vault_name}:{rel_path}"
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                blocks = parse_markdown_blocks(content)
                file_todos = []
                file_highlights = []
                
                for block in blocks:
                    lines = block.content.split('\n')
                    for line in lines:
                        if "- [ ]" in line or "- [x]" in line or "* [ ]" in line or "* [x]" in line:
                            file_todos.append(line.strip())
                        elif any(tag in line.lower() for tag in ['#idea', '#task', '#research', '#meeting']):
                            file_highlights.append(line.strip())
                                
                if file_todos:
                    all_todos.append(f"### {display_path}\n" + "\n".join(file_todos))
                if file_highlights:
                    all_highlights.append(f"### {display_path}\n" + "\n".join(file_highlights))
                    
            except Exception as e:
                pass
                
        if all_todos:
            digest.append("## Pending & Completed Tasks\n")
            digest.append("\n\n".join(all_todos) + "\n")
            
        if all_highlights:
            digest.append("## Highlights (#idea, #research, #meeting)\n")
            digest.append("\n\n".join(all_highlights) + "\n")
            
        if not all_todos and not all_highlights:
            digest.append("No actionable items or highlights found in recently modified notes.")
            
        return "\n".join(digest)
