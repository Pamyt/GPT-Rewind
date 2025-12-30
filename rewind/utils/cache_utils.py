"""Cache utils for rewind"""
import os
import json
import hashlib
from typing import Optional, Any
from pathlib import Path

CACHE_DIR = ".rewind_cache"

class CacheManager:
    """Simple file-based cache manager"""

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, file_path: str, function_name: str) -> str:
        """Generate a unique cache key based on file path and function name"""
        abs_path = os.path.abspath(file_path)
        key_str = f"{abs_path}:{function_name}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, file_path: str, function_name: str) -> Optional[Any]:
        """Get cached result if valid"""
        cache_key = self._get_cache_key(file_path, function_name)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as file_handle:
                cache_data = json.load(file_handle)

            # Check if source file has changed
            current_mtime = os.path.getmtime(file_path)
            if current_mtime != cache_data.get('mtime'):
                return None

            return cache_data.get('data')
        except (OSError, json.JSONDecodeError, AttributeError):
            return None

    def set(self, file_path: str, function_name: str, data: Any):
        """Save result to cache"""
        cache_key = self._get_cache_key(file_path, function_name)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            current_mtime = os.path.getmtime(file_path)
            cache_data = {
                'mtime': current_mtime,
                'data': data
            }

            with open(cache_file, 'w', encoding='utf-8') as file_handle:
                json.dump(cache_data, file_handle, ensure_ascii=False)
        except (OSError, json.JSONDecodeError, AttributeError):
            pass

_cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance"""
    return _cache_manager
