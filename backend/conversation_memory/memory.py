from __future__ import annotations

from typing import Any, Dict, List


class ConversationMemory:
    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def add(self, payload: Dict[str, Any]) -> None:
        self.entries.append(payload)

    def latest(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.entries[-limit:]

    def summary(self) -> Dict[str, Any]:
        return {
            "entry_count": len(self.entries),
            "recent_transcripts": [entry.get("transcript", "") for entry in self.latest(3)],
        }
