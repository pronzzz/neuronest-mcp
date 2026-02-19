import os
import re
from pathlib import Path
from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator

def register(mcp: FastMCP, validator: VaultValidator):
    
    LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
    
    @mcp.tool()
    def get_backlinks(note_name: str) -> str:
        base_name = Path(note_name).stem.lower()
        backlinks = []
        
        for vault_name, vault_root in validator.get_all_vaults():
            for root, dirs, files in os.walk(vault_root):
                if '.git' in root or '.obsidian' in root or '.neuronest' in root:
                    continue
                    
                for file in files:
                    if file.lower().endswith(('.md', '.markdown', '.txt')):
                        filepath = Path(root) / file
                        rel_path = validator.to_relative(filepath)
                        display_path = rel_path if vault_name == "default" and len(validator.vaults) == 1 else f"{vault_name}:{rel_path}"
                        
                        if rel_path.lower() == note_name.lower() or file.lower() == note_name.lower():
                            continue
                            
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            links = LINK_PATTERN.findall(content)
                            for link in links:
                                link_base = link.split('|')[0].split('#')[0]
                                if link_base.lower().strip() == base_name:
                                    backlinks.append(display_path)
                                    break
                        except Exception:
                            pass
                        
        if not backlinks:
            return f"No backlinks found pointing to '{note_name}'."
            
        return f"Notes linking to '{note_name}':\n" + "\n".join(f"- {l}" for l in backlinks)

    @mcp.tool()
    def get_related_notes(note_name: str) -> str:
        filepath = validator.validate_path(note_name, ensure_exists=False)
        if not filepath.exists():
            return f"Note not found: {note_name}"
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"Error reading {note_name}: {e}"
            
        outbound_links = LINK_PATTERN.findall(content)
        outbound = [l.split('|')[0].split('#')[0].strip() for l in outbound_links]
        
        TAG_PATTERN = re.compile(r'(?<=^|[\s])#(\w+)')
        tags = set(TAG_PATTERN.findall(content))
        
        related_by_tag = []
        
        for vault_name, vault_root in validator.get_all_vaults():
            for root, dirs, files in os.walk(vault_root):
                if '.git' in root or '.obsidian' in root or '.neuronest' in root:
                    continue
                for file in files:
                    if file.lower().endswith(('.md', '.markdown', '.txt')):
                        other_filepath = Path(root) / file
                        rel_path = validator.to_relative(other_filepath)
                        display_path = rel_path if vault_name == "default" and len(validator.vaults) == 1 else f"{vault_name}:{rel_path}"
                        
                        if other_filepath.resolve() == filepath.resolve():
                            continue
                        try:
                            with open(other_filepath, 'r', encoding='utf-8') as f:
                                other_content = f.read()
                                if tags:
                                    other_tags = set(TAG_PATTERN.findall(other_content))
                                    shared = tags.intersection(other_tags)
                                    if shared:
                                        related_by_tag.append((display_path, len(shared), shared))
                        except Exception:
                            pass
                            
        related_by_tag.sort(key=lambda x: x[1], reverse=True)
        
        lines = [f"# Related Notes for {note_name}"]
        if outbound:
            lines.append("\n## Outbound Links:")
            for l in outbound:
                lines.append(f"- {l}")
        if related_by_tag:
            lines.append("\n## Shared Tags:")
            for dp, count, shared in related_by_tag[:10]:
                lines.append(f"- {dp} (Shared tags: {', '.join(shared)})")
                
        if len(lines) == 1:
            return "No related notes or links found."
        
        return "\n".join(lines)
