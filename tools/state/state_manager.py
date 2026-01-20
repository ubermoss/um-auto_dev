"""State manager for tracking conversation state and execution context."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class StateManager:
    """Manages persistent state across conversation turns."""

    def __init__(self, state_file: str = "conversation_state.json"):
        """Initialize state manager with a state file path."""
        self.state_file = Path(state_file)
        self.state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file or create new state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.state_file}, creating new state")
                return self._create_new_state()
        return self._create_new_state()

    def _create_new_state(self) -> Dict[str, Any]:
        """Create a new empty state structure."""
        return {
            "conversation_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_file": None,
            "current_branch": None,
            "execution_history": [],
            "context": {},
            "pending_actions": []
        }

    def save_state(self) -> None:
        """Save current state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, indent=2, fp=f)

    def update_context(self, key: str, value: Any) -> None:
        """Update a specific context value."""
        self.state["context"][key] = value
        self.save_state()

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.state["context"].get(key, default)

    def add_execution(self, command: str, result: Dict[str, Any]) -> None:
        """Record an execution in history."""
        execution = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result
        }
        self.state["execution_history"].append(execution)
        self.save_state()

    def set_current_file(self, filepath: str) -> None:
        """Set the current working file."""
        self.state["current_file"] = filepath
        self.save_state()

    def get_current_file(self) -> Optional[str]:
        """Get the current working file."""
        return self.state.get("current_file")

    def set_current_branch(self, branch: str) -> None:
        """Set the current git branch."""
        self.state["current_branch"] = branch
        self.save_state()

    def get_current_branch(self) -> Optional[str]:
        """Get the current git branch."""
        return self.state.get("current_branch")

    def add_pending_action(self, action: Dict[str, Any]) -> None:
        """Add an action to the pending queue."""
        self.state["pending_actions"].append(action)
        self.save_state()

    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get all pending actions."""
        return self.state.get("pending_actions", [])

    def clear_pending_actions(self) -> None:
        """Clear all pending actions."""
        self.state["pending_actions"] = []
        self.save_state()

    def get_last_execution(self) -> Optional[Dict[str, Any]]:
        """Get the most recent execution from history."""
        history = self.state.get("execution_history", [])
        return history[-1] if history else None

    def clear_history(self) -> None:
        """Clear execution history."""
        self.state["execution_history"] = []
        self.save_state()
