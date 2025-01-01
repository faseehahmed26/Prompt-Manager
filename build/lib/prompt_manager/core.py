from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from packaging.version import parse as parse_version
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PromptWatcher(FileSystemEventHandler):
    """Handles file system events for the prompts directory."""
    def __init__(self, manager):
        self.manager = manager

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".json"):
            self.manager.reload_prompt(Path(event.src_path).stem)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".json"):
            self.manager.reload_prompt(Path(event.src_path).stem)


class PromptVersion:
    def __init__(self, version: str, template: str, variables: List[str], description: str):
        self.version = version
        self.template = template
        self.variables = variables
        self.description = description
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "template": self.template,
            "variables": self.variables,
            "description": self.description,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptVersion':
        version = cls(
            version=data["version"],
            template=data["template"],
            variables=data["variables"],
            description=data["description"]
        )
        version.created_at = data.get("created_at", datetime.now().isoformat())
        return version


class Prompt:
    def __init__(self, name: str):
        self.name = name
        self.versions: Dict[str, PromptVersion] = {}
        self.current_version: Optional[str] = None

    def add_version(self, version: PromptVersion) -> None:
        self.versions[version.version] = version
        if not self.current_version or parse_version(version.version) > parse_version(self.current_version):
            self.current_version = version.version

    def get_version(self, version: Optional[str] = None) -> PromptVersion:
        version_key = version or self.current_version
        if not version_key:
            raise ValueError(f"No version specified and no current version set for prompt '{self.name}'")
        if version_key not in self.versions:
            raise KeyError(f"Version '{version_key}' not found for prompt '{self.name}'")
        return self.versions[version_key]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "current_version": self.current_version,
            "versions": [version.to_dict() for version in self.versions.values()]
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'Prompt':
        prompt = cls(name)
        prompt.current_version = data.get("current_version")
        for version_data in data["versions"]:
            version = PromptVersion.from_dict(version_data)
            prompt.versions[version.version] = version
        return prompt


class PromptManager:
    def __init__(self, prompts_dir: Path):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.prompts: Dict[str, Prompt] = {}
        self._load_prompts()
        self._start_watcher()

    def _load_prompts(self) -> None:
        for prompt_file in self.prompts_dir.glob("*.json"):
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prompt = Prompt.from_dict(prompt_file.stem, data)
                    self.prompts[prompt.name] = prompt
            except Exception as e:
                print(f"Error loading prompt file {prompt_file}: {e}")

    def _start_watcher(self) -> None:
        """Start a file system watcher to monitor changes in the prompts directory."""
        event_handler = PromptWatcher(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.prompts_dir), recursive=False)
        self.observer.start()

    def add_prompt_version(self, name: str, version: str, template: str, variables: List[str], description: str) -> None:
        for var in variables:
            if f"{{{var}}}" not in template:
                raise ValueError(f"Variable '{var}' declared but not used in template")
        if name not in self.prompts:
            self.prompts[name] = Prompt(name)
        prompt_version = PromptVersion(version, template, variables, description)
        self.prompts[name].add_version(prompt_version)
        self._save_prompt(name)

    def get_prompt(self, name: str, variables: Dict[str, Any], version: Optional[str] = None) -> str:
        if name not in self.prompts:
            raise KeyError(f"Prompt '{name}' not found")
        prompt = self.prompts[name]
        prompt_version = prompt.get_version(version)
        missing_vars = set(prompt_version.variables) - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        return prompt_version.template.format(**variables)

    def reload_prompt(self, name: str) -> None:
        file_path = self.prompts_dir / f"{name}.json"
        if not file_path.exists():
            print(f"Prompt file {file_path} does not exist.")
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                prompt = Prompt.from_dict(name, data)
                self.prompts[name] = prompt
                print(f"Prompt '{name}' reloaded successfully.")
        except Exception as e:
            print(f"Error reloading prompt file {file_path}: {e}")

    def _save_prompt(self, name: str) -> None:
        file_path = self.prompts_dir / f"{name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.prompts[name].to_dict(), f, indent=2, ensure_ascii=False)

    def list_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "current_version": prompt.current_version,
                "versions": list(prompt.versions.keys())
            }
            for name, prompt in self.prompts.items()
        ]
