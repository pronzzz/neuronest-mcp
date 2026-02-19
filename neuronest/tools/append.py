import datetime
from fastmcp import FastMCP
from neuronest.core.vault_validator import VaultValidator

def register(mcp: FastMCP, validator: VaultValidator):
    
    @mcp.tool()
    def append_to_daily_note(text: str) -> str:
        """
        Appends text to today's daily note. Creates the note if it doesn't exist.
        The daily note is stored in a 'Daily' folder in the root of the default vault, formatted as YYYY-MM-DD.md.
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        _, vault_root, _ = validator._resolve_vault("default:.")
        
        daily_folder = vault_root / "Daily"
        daily_folder.mkdir(exist_ok=True)
        
        filename = f"Daily/{today}.md"
        filepath = validator.validate_path(filename, ensure_exists=False)
        
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        is_new = not filepath.exists()
        
        with open(filepath, 'a', encoding='utf-8') as f:
            if is_new:
                f.write(f"# Daily Note: {today}\n\n")
            f.write(f"- [{timestamp}] {text}\n")
            
        return f"Appended to {filename}"
