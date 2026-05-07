import importlib
from typing import Callable
import sys
import os
import time
import threading

def _reload_with_submodules(module):
    package = module.__name__.rsplit(".", 1)[0]
    submods = [
        mod for name, mod in sys.modules.items()
        if name.startswith(package + ".") and name != module.__name__
    ]
    for submod in submods:
        importlib.reload(submod)
    return importlib.reload(module)


class Event():
    def __init__(self, handler: 'Events_Handler', name:str, data:dict=None):
        self._handler = handler
        self.name = name.lower().strip()
        if(data is None): data = {}
        self.data = data
    def consume(self) -> None: self._handler.consume(self)
    def matches(self, name:str) -> bool: return (self.name == name.lower().strip())
    def __repr__(self): return f"Event(name='{self.name}', data={self.data})"
class Events_Handler():
    def __init__(self):

        self._hooks: dict[str, tuple[Callable[[Event], Event], object]] = {}
        self._current_events:list[Event] = []
        self._new_events: list[Event] = []
        self._lock = threading.Lock()

    # Emit an event for other items to listen to next tick
    def emit(self, name: str, data: dict = None) -> None:
        with self._lock: self._new_events.append(Event(self, name, data))

    # Emits instantly, items already processed this tick will not receive it
    def emit_now(self, name: str, data: dict = None) -> None:
        with self._lock: self._current_events.append(Event(self, name, data))

    # If an item has a hook for this event, it will run instantly and receive the return value, otherwise returns None
    def request(self, name: str, data: dict = None) -> Event | None:
        entry = self._hooks.get(name.lower().strip())
        if entry is None: return None
        return entry[0](Event(self, name, data))

    # Create a new hook for an event, if it already exists it will raise an exception
    def hook(self, name:str, func: Callable[[Event], Event], owner: object = None) -> None:
        key = name.lower().strip()
        if key in self._hooks: raise Exception(f"Hook for '{name}' already exists")
        self._hooks[key] = (func, owner)

    # Remove a hook, raises an exception if it doesn't exist
    def unhook(self, name:str) -> None:
        key = name.lower().strip()
        if key not in self._hooks: raise Exception(f"Hook for '{name}' does not exist")
        del self._hooks[key]

    # Remove all hooks registered by a given owner
    def unhook_all(self, owner: object) -> None:
        to_remove = [name for name, (_, o) in self._hooks.items() if o is owner]
        for name in to_remove: del self._hooks[name]

    # Returns the current event list, iterate over it to process events
    def get_events(self, name: str = None) -> list[Event]:
        with self._lock:
            if name is None: return list(self._current_events)
            return [e for e in self._current_events if e.matches(name)]

    # Remove an event so subsequent items won't receive it
    def consume(self, event: Event) -> None:
        with self._lock:
            try: self._current_events.remove(event)
            except ValueError: raise Exception("Event not found in current events")

    def tick(self):
        with self._lock:
            self._current_events = self._new_events
            self._new_events = []

class Run():
    def __init__(self, events_handler: Events_Handler, import_path: str, class_name: str):
        self.events_handler = events_handler
        self.import_path = import_path
        self.class_name = class_name
        self.run_me = True

        self._module = importlib.import_module(import_path)
        self._item: RunChild = getattr(self._module, class_name)(self, events_handler)
        self._watch_mtimes: dict[str, float] = {}
        self._start_time = time.time()
        self.status: str = ""

    def _get_watch_files(self, extensions: tuple[str]) -> list[str]:
        folder = os.path.dirname(self._module.__file__)
        files = []
        for root, _, filenames in os.walk(folder):
            for f in filenames:
                if f.endswith(extensions):
                    files.append(os.path.join(root, f))
        return files

    # Returns True if any watched file has changed since the last call
    def check_file_changed(self, extensions: tuple[str] = (".py",)) -> bool:
        changed = False
        for path in self._get_watch_files(extensions):
            mtime = os.path.getmtime(path)
            baseline = self._watch_mtimes.get(path, self._start_time)
            if mtime > baseline:
                changed = True
            self._watch_mtimes[path] = mtime
        return changed

    def start(self):
        self.status = ""
        self._item.start()
    def stop(self):
        self.run_me = False
        self.events_handler.unhook_all(self._item)
        self._item.stop()
    def tick(self): self._item.tick()

    def restart(self, no_start=False):
        self.stop()
        self._module = _reload_with_submodules(self._module)
        self._item = getattr(self._module, self.class_name)(self, self.events_handler)
        self.run_me = (not no_start)
        if not no_start: self.start()

class RunChild():
    def __init__(self, parent: Run, events_handler: Events_Handler):
        self.parent = parent
        self.events_handler = events_handler\
    
    def set_status(self, status:str): self.parent.status = status

    def start(self): pass
    def stop(self): pass
    def tick(self): pass