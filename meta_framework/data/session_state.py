"""Session state management for iteration loops."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class SessionState:
    """
    Manages persistent state for iteration sessions.

    This enables:
    - Resuming sessions after context runs out
    - Token-efficient summaries
    - Tracking progress across iterations
    - Learning from past projects
    """

    def __init__(self, session_id: str, project_path: str):
        """Initialize session state."""
        self.session_id = session_id
        self.project_path = Path(project_path)
        self.state_file = self.project_path / "iterations" / session_id / "session_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state or create new
        self.state = self._load_or_create()

    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing state or create new."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)

        return self._create_new_state()

    def _create_new_state(self) -> Dict[str, Any]:
        """Create new session state structure."""
        return {
            "session_id": self.session_id,
            "project_path": str(self.project_path),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),

            # Project understanding
            "project": {
                "type": None,  # automotive_visualization, architecture, etc.
                "goal": None,  # User's stated goal
                "domain": None,  # Inferred domain
                "roadmap_chosen": None,  # Which option was selected
            },

            # Progress tracking
            "current_iteration": 0,
            "iterations_completed": [],

            # System evolution
            "capabilities_added": [],
            "knowledge_gained": [],

            # Decision tracking
            "pending_decisions": [],
            "research_needed": [],

            # Quick resume info
            "digest": {
                "summary": "New session",
                "current_score": 0.0,
                "last_render": None,
                "next_action": "Bootstrap project understanding"
            }
        }

    def save(self):
        """Save current state to file."""
        self.state["last_updated"] = datetime.now().isoformat()

        # Update digest for quick resume
        self._update_digest()

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _update_digest(self):
        """Update quick-resume digest."""
        iterations = self.state["iterations_completed"]

        if not iterations:
            self.state["digest"] = {
                "summary": "No iterations yet",
                "current_score": 0.0,
                "last_render": None,
                "next_action": "Run first iteration"
            }
            return

        last = iterations[-1]
        capabilities = self.state["capabilities_added"]

        self.state["digest"] = {
            "summary": f"{len(iterations)} iterations, score {last['score_after']:.0%}",
            "current_score": last["score_after"],
            "last_render": last.get("render_path"),
            "capabilities_built": len(capabilities),
            "next_action": last.get("next_action", "Continue iteration")
        }

    def set_project_info(self, project_type: str, goal: str, domain: str):
        """Set project understanding."""
        self.state["project"]["type"] = project_type
        self.state["project"]["goal"] = goal
        self.state["project"]["domain"] = domain
        self.save()

    def set_roadmap(self, roadmap: str):
        """Set chosen roadmap/strategy."""
        self.state["project"]["roadmap_chosen"] = roadmap
        self.save()

    def add_iteration(self, iteration_data: Dict[str, Any]):
        """Add completed iteration."""
        self.state["current_iteration"] = iteration_data["iteration"]

        # Store compact iteration info
        compact = {
            "iteration": iteration_data["iteration"],
            "timestamp": datetime.now().isoformat(),
            "summary": iteration_data.get("summary", ""),
            "score_before": iteration_data.get("score_before", 0),
            "score_after": iteration_data.get("score_after", 0),
            "improvement": iteration_data.get("score_after", 0) - iteration_data.get("score_before", 0),
            "key_changes": iteration_data.get("key_changes", []),
            "system_enhancements": iteration_data.get("system_enhancements", []),
            "insights": iteration_data.get("insights", []),
            "render_path": iteration_data.get("render_path"),
            "next_action": iteration_data.get("next_action")
        }

        self.state["iterations_completed"].append(compact)
        self.save()

    def add_capability(self, capability_name: str, description: str):
        """Track new capability added."""
        self.state["capabilities_added"].append({
            "name": capability_name,
            "description": description,
            "added_at": datetime.now().isoformat(),
            "iteration": self.state["current_iteration"]
        })
        self.save()

    def add_knowledge(self, insight: str, category: str = "general"):
        """Track knowledge gained."""
        self.state["knowledge_gained"].append({
            "insight": insight,
            "category": category,
            "learned_at": datetime.now().isoformat(),
            "iteration": self.state["current_iteration"]
        })
        self.save()

    def add_pending_decision(self, question: str, context: str, options: List[str]):
        """Add decision that needs human input."""
        self.state["pending_decisions"].append({
            "question": question,
            "context": context,
            "options": options,
            "added_at": datetime.now().isoformat()
        })
        self.save()

    def add_research_need(self, topic: str, reason: str):
        """Track research that would help."""
        self.state["research_needed"].append({
            "topic": topic,
            "reason": reason,
            "added_at": datetime.now().isoformat()
        })
        self.save()

    def clear_pending_decisions(self):
        """Clear pending decisions (after human answers)."""
        self.state["pending_decisions"] = []
        self.save()

    def get_resume_info(self) -> Dict[str, Any]:
        """Get information for resuming session."""
        iterations = self.state["iterations_completed"]

        if not iterations:
            return {
                "status": "new",
                "message": "New session, no iterations yet"
            }

        last = iterations[-1]

        # Create concise summary
        summary = {
            "session_id": self.session_id,
            "project_type": self.state["project"]["type"],
            "goal": self.state["project"]["goal"],
            "roadmap": self.state["project"]["roadmap_chosen"],

            "progress": {
                "iterations": len(iterations),
                "current_score": last["score_after"],
                "total_improvement": last["score_after"] - iterations[0]["score_before"],
                "last_render": last.get("render_path")
            },

            "system_evolution": {
                "capabilities_added": len(self.state["capabilities_added"]),
                "capability_list": [c["name"] for c in self.state["capabilities_added"]],
                "key_learnings": [k["insight"] for k in self.state["knowledge_gained"][-3:]]  # Last 3
            },

            "recent_work": {
                "last_iteration_summary": last["summary"],
                "last_changes": last["key_changes"],
                "last_insights": last["insights"]
            },

            "next_steps": {
                "suggested_action": last.get("next_action", "Continue iteration"),
                "pending_decisions": len(self.state["pending_decisions"]),
                "research_needed": len(self.state["research_needed"])
            }
        }

        return summary

    def get_full_history(self) -> List[Dict[str, Any]]:
        """Get complete iteration history."""
        return self.state["iterations_completed"]

    def export_for_human_review(self) -> Dict[str, Any]:
        """Export comprehensive review package."""
        iterations = self.state["iterations_completed"]

        if not iterations:
            return {"message": "No iterations to review"}

        first = iterations[0]
        last = iterations[-1]

        return {
            "session_summary": {
                "session_id": self.session_id,
                "project": self.state["project"],
                "duration": f"{len(iterations)} iterations",
                "initial_score": first["score_before"],
                "final_score": last["score_after"],
                "total_improvement": last["score_after"] - first["score_before"],
                "improvement_percentage": (last["score_after"] - first["score_before"]) * 100
            },

            "iteration_history": [
                {
                    "iteration": it["iteration"],
                    "summary": it["summary"],
                    "score_change": f"{it['score_before']:.0%} → {it['score_after']:.0%}",
                    "improvement": f"+{it['improvement']:.0%}",
                    "key_changes": it["key_changes"]
                }
                for it in iterations
            ],

            "system_enhancements": self.state["capabilities_added"],

            "knowledge_gained": self.state["knowledge_gained"],

            "pending_decisions": self.state["pending_decisions"],

            "research_needs": self.state["research_needed"],

            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on session."""
        recommendations = []

        iterations = self.state["iterations_completed"]
        if not iterations:
            return ["Run first iteration"]

        last = iterations[-1]
        score = last["score_after"]

        if score >= 0.85:
            recommendations.append("Quality threshold achieved - ready for review")
        elif score < 0.70:
            recommendations.append("Continue iterations - significant improvement possible")

        if self.state["pending_decisions"]:
            recommendations.append(f"Answer {len(self.state['pending_decisions'])} pending decisions")

        if self.state["research_needed"]:
            recommendations.append(f"Consider researching {len(self.state['research_needed'])} topics")

        if len(iterations) >= 10:
            recommendations.append("Long session - consider human review checkpoint")

        return recommendations
