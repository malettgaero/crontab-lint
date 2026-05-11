"""Track and persist a history of validated crontab expressions."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_HISTORY_PATH = os.path.expanduser("~/.crontab_lint_history.json")


@dataclass
class HistoryEntry:
    expression: str
    valid: bool
    human_readable: Optional[str]
    errors: List[str]
    checked_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class History:
    entries: List[HistoryEntry] = field(default_factory=list)

    def add(self, entry: HistoryEntry) -> None:
        self.entries.append(entry)

    def last(self, n: int = 10) -> List[HistoryEntry]:
        return self.entries[-n:]

    def filter_valid(self) -> List[HistoryEntry]:
        return [e for e in self.entries if e.valid]

    def filter_invalid(self) -> List[HistoryEntry]:
        return [e for e in self.entries if not e.valid]

    def clear(self) -> None:
        self.entries.clear()


def load_history(path: str = DEFAULT_HISTORY_PATH) -> History:
    """Load history from a JSON file, returning an empty History if missing."""
    if not os.path.exists(path):
        return History()
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    entries = [HistoryEntry(**e) for e in raw.get("entries", [])]
    return History(entries=entries)


def save_history(history: History, path: str = DEFAULT_HISTORY_PATH) -> None:
    """Persist history to a JSON file."""
    data = {"entries": [asdict(e) for e in history.entries]}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def record(
    expression: str,
    valid: bool,
    human_readable: Optional[str] = None,
    errors: Optional[List[str]] = None,
    path: str = DEFAULT_HISTORY_PATH,
) -> HistoryEntry:
    """Append a new entry to the history file and return it."""
    history = load_history(path)
    entry = HistoryEntry(
        expression=expression,
        valid=valid,
        human_readable=human_readable,
        errors=errors or [],
    )
    history.add(entry)
    save_history(history, path)
    return entry
