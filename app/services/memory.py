from typing import Dict, List
from collections import defaultdict


class InMemorySessionMemory:
    def __init__(self, max_pairs: int = 5):
        self.max_pairs = max_pairs
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        self.sessions[session_id].append({"user": user_msg, "assistant": assistant_msg})
        self.sessions[session_id] = self.sessions[session_id][-self.max_pairs:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])
