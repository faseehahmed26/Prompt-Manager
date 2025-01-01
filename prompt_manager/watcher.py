from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path


class PromptWatcher(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".json"):
            self.manager.reload_prompt(Path(event.src_path).stem)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".json"):
            self.manager.reload_prompt(Path(event.src_path).stem)


def start_watching(manager, directory):
    event_handler = PromptWatcher(manager)
    observer = Observer()
    observer.schedule(event_handler, str(directory), recursive=False)
    observer.start()
