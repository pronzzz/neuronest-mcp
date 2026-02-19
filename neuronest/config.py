import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Union

class NeuroNestConfig(BaseModel):
    vaults: Dict[str, Path] = Field(
        default_factory=lambda: {"default": Path(os.environ.get("NEURONEST_VAULT_PATH", "."))},
        description="Dictionary of vault names and their absolute paths"
    )

    @field_validator("vaults", mode='before')
    @classmethod
    def parse_vaults(cls, v):
        if isinstance(v, (str, Path)):
            return {"default": Path(v)}
        if isinstance(v, dict):
            return {name: Path(path) for name, path in v.items()}
        return v
        
    @field_validator("vaults")
    @classmethod
    def validate_vault_paths(cls, v: Dict[str, Path]) -> Dict[str, Path]:
        resolved_vaults = {}
        for name, path in v.items():
            resolved = path.resolve()
            if not resolved.exists():
                raise ValueError(f"Vault path does not exist: {resolved}")
            if not resolved.is_dir():
                raise ValueError(f"Vault path is not a directory: {resolved}")
            resolved_vaults[name] = resolved
        return resolved_vaults

def load_config() -> NeuroNestConfig:
    return NeuroNestConfig()
