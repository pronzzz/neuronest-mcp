from pathlib import Path

class SecurityError(Exception):
    """Raised when an operation attempts to violate vault boundary."""
    pass

class VaultValidator:
    def __init__(self, vaults: dict[str, Path]):
        self.vaults = vaults
        self.default_vault = list(self.vaults.keys())[0] if self.vaults else None

    def _resolve_vault(self, filepath: str) -> tuple[str, Path, str]:
        """Parses 'vault_name:path' into (vault_name, vault_root, rel_path)."""
        if ':' in filepath and not filepath.startswith(('C:', 'D:', 'E:')): # very naive windows drive check
            parts = filepath.split(':', 1)
            vault_name = parts[0]
            if vault_name in self.vaults:
                return vault_name, self.vaults[vault_name], parts[1]
                
        if not self.default_vault:
            raise SecurityError("No vaults configured")
            
        return self.default_vault, self.vaults[self.default_vault], filepath

    def validate_path(self, filepath: str | Path, ensure_exists: bool = False) -> Path:
        filepath_str = str(filepath)
        vault_name, vault_root, rel_path = self._resolve_vault(filepath_str)
        
        try:
            target_path = vault_root / rel_path
            resolved_target = target_path.resolve()
        except Exception as e:
            raise SecurityError(f"Invalid path representation: {e}")

        try:
            resolved_target.relative_to(vault_root)
        except ValueError:
            raise SecurityError(f"Directory traversal attempt blocked: {filepath_str}")

        if resolved_target.suffix.lower() not in ('.md', '.markdown', '.txt'):
            raise SecurityError(f"Only markdown/text files are allowed: {filepath_str}")

        if ensure_exists and not resolved_target.exists():
            raise FileNotFoundError(f"File not found: {filepath_str}")

        return resolved_target

    def to_relative(self, filepath: Path) -> str:
        for name, root in self.vaults.items():
            try:
                rel = filepath.relative_to(root)
                if len(self.vaults) > 1:
                    return f"{name}:{rel}"
                return str(rel)
            except ValueError:
                continue
        return str(filepath)
        
    def get_all_vaults(self):
        return self.vaults.items()
