from threading import Lock
import yaml
import os
from pathlib import Path
from typing import Any  # Import Any for type annotations

# CACHE MANAGER CLASS
class CacheManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cache = {}
            return cls._instance

    def set(self, key: str, value: Any) -> None:
        """SET A VARIABLE IN THE CACHE"""
        self._cache[key] = value
        print(f"---{key} ADDED IN CACHE---")

    def get(self, key: str, default = None) -> Any:
        """GET A VARIABLE FROM THE CACHE"""
        print(f"---GETTING {key} FROM CACHE---")
        return self._cache.get(key, default)

    def has(self, key: str) -> bool:
        """CHECK IF A VARIABLE EXISTS IN THE CACHE"""
        return key in self._cache

    def clear(self, key: str = None) -> None:
        """CLEAR A CATEGORY FROM THE CACHE"""
        if key:
            self._cache.pop(key, None)
            print(f"---{key} CLEARED FROM CACHE---")
        else:
            self._cache = {}
            print(f"---ALL CATEGORIES CLEARED FROM CACHE---")

    def append_to_list(self, key: str, value: Any) -> bool:
        """APPEND A VALUE TO A LIST IN THE CACHE"""
        if key in self._cache:
            if isinstance(self._cache[key], list):
                self._cache[key].append(value)
                print(f"---APPENDED VALUE TO {key} IN CACHE---")
                return True
            else:
                print(f"---ERROR: {key} IS NOT A LIST---")
                return False
        else:
            self._cache[key] = [value]
            print(f"---CREATED NEW LIST WITH VALUE IN {key}---")
            return True

    def remove_from_list(self, key: str, value: Any) -> bool:
        """REMOVE A VALUE FROM A LIST IN THE CACHE"""
        if key in self._cache and isinstance(self._cache[key], list):
            try:
                self._cache[key].remove(value)
                print(f"---REMOVED VALUE FROM {key} IN CACHE---")
                return True
            except ValueError:
                print(f"---VALUE NOT FOUND IN {key}---")
                return False
        else:
            print(f"---ERROR: {key} NOT FOUND OR NOT A LIST---")
            return False

# FUNCTION TO LOAD PROMPTS
def load_prompts(path: Path) -> dict:
    print(f"---LOADING PROMPTS FROM {path}---")
    with open(path, 'r') as file:
        prompts = yaml.safe_load(file)
    return prompts

def process_directory(directory_path):
    results = []

    # Process TXT files for job descriptions
    for file in os.listdir(directory_path):
        if file.endswith(".txt"):
            file_path = os.path.join(directory_path, file)
            with open(file_path, "r") as f:
                content = f.read()
                results.append({
                    "name": file,
                    "content": content
                })
    return results