import os
import json
import numpy as np
from pathlib import Path
from neuronest.core.vault_validator import VaultValidator

class SemanticIndex:
    def __init__(self, validator: VaultValidator):
        self.validator = validator
        self._model = None
        self.index_data = {}
        self._load_all_caches()
        
    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                print("sentence-transformers not installed. Semantic search disabled.")
                self._model = False
        return self._model
        
    def _cache_file(self, vault_root: Path):
        return vault_root / ".neuronest_index.json"
        
    def _load_all_caches(self):
        for name, root in self.validator.get_all_vaults():
            cf = self._cache_file(root)
            if cf.exists():
                try:
                    with open(cf, 'r', encoding='utf-8') as f:
                        self.index_data[name] = json.load(f)
                except Exception:
                    self.index_data[name] = {}
            else:
                self.index_data[name] = {}
                
    def _save_cache(self, vault_name: str, vault_root: Path):
        try:
            with open(self._cache_file(vault_root), 'w', encoding='utf-8') as f:
                json.dump(self.index_data[vault_name], f)
        except Exception:
            pass
            
    def update_index(self):
        if self.model is False:
            return
            
        for vault_name, vault_root in self.validator.get_all_vaults():
            changed = False
            for root, dirs, files in os.walk(vault_root):
                if '.git' in root or '.obsidian' in root or '.neuronest' in root:
                    continue
                    
                for file in files:
                    if file.lower().endswith(('.md', '.markdown', '.txt')):
                        filepath = Path(root) / file
                        try:
                            mtime = filepath.stat().st_mtime
                            rel_path = str(filepath.relative_to(vault_root))
                            
                            idx_map = self.index_data[vault_name]
                            if rel_path in idx_map and idx_map[rel_path]['mtime'] >= mtime:
                                continue
                                
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            summary_text = content[:2000]
                            if not summary_text.strip():
                                continue
                                
                            embedding = self.model.encode(summary_text).tolist()
                            
                            idx_map[rel_path] = {
                                'mtime': mtime,
                                'embedding': embedding
                            }
                            changed = True
                        except Exception:
                            pass
                            
            if changed:
                self._save_cache(vault_name, vault_root)
                
    def search(self, query: str, top_k: int = 5) -> list[str]:
        if self.model is False:
            return []
            
        if not any(self.index_data.values()):
            self.update_index()
            
        query_embedding = self.model.encode(query)
        
        results = []
        for vault_name, idx_map in self.index_data.items():
            for rel_path, data in idx_map.items():
                doc_emb = np.array(data['embedding'])
                norm_q = np.linalg.norm(query_embedding)
                norm_d = np.linalg.norm(doc_emb)
                if norm_q == 0 or norm_d == 0:
                    continue
                similarity = np.dot(query_embedding, doc_emb) / (norm_q * norm_d)
                
                # Format with prefix if multi-vault
                display_path = f"{vault_name}:{rel_path}" if len(self.index_data) > 1 else rel_path
                results.append((similarity, display_path))
            
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k]]
