"""CLI tools for session management."""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.session_state import SessionState
from data.capability_registry import CapabilityRegistry


def list_sessions(project_path: str):
    """List all sessions for a project."""
    project = Path(project_path)
    iterations_dir = project / "iterations"

    if not iterations_dir.exists():
        return {"sessions": []}

    sessions = []
    for session_dir in sorted(iterations_dir.iterdir()):
        if session_dir.is_dir():
            state_file = session_dir / "session_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    digest = state.get("digest", {})
                    sessions.append({
                        "session_id": session_dir.name,
                        "summary": digest.get("summary", "Unknown"),
                        "score": digest.get("current_score", 0),
                        "last_updated": state.get("last_updated", "Unknown")
                    })

    return {"sessions": sessions}


def get_session_info(project_path: str, session_id: str):
    """Get detailed session information."""
    state = SessionState(session_id, project_path)
    return state.get_resume_info()


def export_session_review(project_path: str, session_id: str):
    """Export session for human review."""
    state = SessionState(session_id, project_path)
    return state.export_for_human_review()


def get_capabilities():
    """Get all system capabilities."""
    registry = CapabilityRegistry()
    return registry.export_summary()


def check_capabilities(required: list):
    """Check which capabilities are available."""
    registry = CapabilityRegistry()
    available = registry.check_required_capabilities(required)
    missing = registry.get_missing_capabilities(required)

    return {
        "available": available,
        "missing": missing,
        "all_present": len(missing) == 0
    }


if __name__ == "__main__":
    """Simple CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Session management tools")
    subparsers = parser.add_subparsers(dest="command")

    # List sessions
    list_parser = subparsers.add_parser("list", help="List sessions")
    list_parser.add_argument("project", help="Project path")

    # Get session info
    info_parser = subparsers.add_parser("info", help="Get session info")
    info_parser.add_argument("project", help="Project path")
    info_parser.add_argument("session", help="Session ID")

    # Export review
    review_parser = subparsers.add_parser("review", help="Export session review")
    review_parser.add_argument("project", help="Project path")
    review_parser.add_argument("session", help="Session ID")

    # Capabilities
    cap_parser = subparsers.add_parser("capabilities", help="List capabilities")

    # Check capabilities
    check_parser = subparsers.add_parser("check", help="Check capabilities")
    check_parser.add_argument("required", nargs="+", help="Required capabilities")

    args = parser.parse_args()

    result = None

    if args.command == "list":
        result = list_sessions(args.project)
    elif args.command == "info":
        result = get_session_info(args.project, args.session)
    elif args.command == "review":
        result = export_session_review(args.project, args.session)
    elif args.command == "capabilities":
        result = get_capabilities()
    elif args.command == "check":
        result = check_capabilities(args.required)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))
