"""Action Planner Agent - Decides what changes to make based on evaluation."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class ActionPlanner:
    """
    Plans what actions to take based on visual evaluation feedback.

    This agent translates evaluation feedback into concrete, executable actions.
    It also identifies when the control system needs enhancement.
    """

    def __init__(self):
        """Initialize the action planner."""
        self.planning_history: List[Dict[str, Any]] = []
        self.system_enhancement_requests: List[Dict[str, Any]] = []

    def plan_actions(
        self,
        evaluation: Dict[str, Any],
        available_capabilities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Plan actions based on evaluation feedback.

        Args:
            evaluation: The evaluation results from VisualEvaluator
            available_capabilities: What the control system can currently do

        Returns:
            Action plan with specific changes to make
        """
        plan = {
            "iteration": evaluation.get("iteration", 0),
            "timestamp": datetime.now().isoformat(),
            "evaluation_score": evaluation.get("analysis", {}).get("overall_score", 0),
            "actions": [],
            "system_enhancements_needed": [],
            "reasoning": [],
            "estimated_impact": 0.0,
            "confidence": 0.0
        }

        analysis = evaluation.get("analysis", {})

        # Process critical issues first (highest priority)
        critical_issues = analysis.get("critical_issues", [])
        for issue in critical_issues:
            action = self._create_action_from_issue(
                issue,
                "critical",
                available_capabilities
            )
            if action["can_execute"]:
                plan["actions"].append(action)
                plan["reasoning"].append(f"Critical: {issue['issue']}")
            else:
                # Need system enhancement
                enhancement = {
                    "reason": f"Cannot fix: {issue['issue']}",
                    "missing_capability": action["missing_capability"],
                    "priority": "high",
                    "suggested_implementation": action.get("suggestion", "")
                }
                plan["system_enhancements_needed"].append(enhancement)
                self.system_enhancement_requests.append(enhancement)

        # Process improvements (if we have capacity)
        if len(plan["actions"]) < 3:  # Leave room for improvements
            improvements = analysis.get("improvements", [])
            for improvement in improvements[:3 - len(plan["actions"])]:
                action = self._create_action_from_improvement(
                    improvement,
                    available_capabilities
                )
                if action["can_execute"]:
                    plan["actions"].append(action)
                    plan["reasoning"].append(f"Improve: {improvement['improvement']}")

        # Estimate total impact
        if plan["actions"]:
            total_impact = sum(a.get("expected_impact", 0) for a in plan["actions"])
            plan["estimated_impact"] = min(total_impact, 0.3)  # Cap at 30% improvement per iteration
            plan["confidence"] = self._calculate_confidence(plan["actions"])

        self.planning_history.append(plan)
        return plan

    def _create_action_from_issue(
        self,
        issue: Dict[str, Any],
        priority: str,
        capabilities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Convert an issue into an executable action."""

        action = {
            "type": "fix_issue",
            "priority": priority,
            "issue": issue["issue"],
            "fix": issue["fix"],
            "can_execute": False,
            "implementation": {},
            "expected_impact": 0.15  # High impact for critical fixes
        }

        # Parse the fix to determine if we can execute it
        fix_text = issue["fix"].lower()

        # Lighting adjustments
        if "light" in fix_text and "intensity" in fix_text:
            if "lighting" in capabilities:
                action["can_execute"] = True
                action["implementation"] = {
                    "system": "blender",
                    "component": "lighting",
                    "operation": "adjust_intensity",
                    "parameters": self._extract_light_parameters(issue["fix"])
                }
            else:
                action["missing_capability"] = "lighting_control"
                action["suggestion"] = "Implement lighting adjustment in BlenderTools"

        # Material adjustments
        elif "material" in fix_text or "roughness" in fix_text or "metallic" in fix_text:
            if "materials" in capabilities:
                action["can_execute"] = True
                action["implementation"] = {
                    "system": "blender",
                    "component": "materials",
                    "operation": "adjust_material",
                    "parameters": self._extract_material_parameters(issue["fix"])
                }
            else:
                action["missing_capability"] = "material_control"

        # Camera adjustments
        elif "camera" in fix_text or "angle" in fix_text or "framing" in fix_text:
            if "camera" in capabilities:
                action["can_execute"] = True
                action["implementation"] = {
                    "system": "blender",
                    "component": "camera",
                    "operation": "adjust_camera",
                    "parameters": self._extract_camera_parameters(issue["fix"])
                }
            else:
                action["missing_capability"] = "camera_control"

        # Render settings
        elif "sample" in fix_text or "denoise" in fix_text or "resolution" in fix_text:
            if "render_settings" in capabilities:
                action["can_execute"] = True
                action["implementation"] = {
                    "system": "blender",
                    "component": "render",
                    "operation": "adjust_settings",
                    "parameters": self._extract_render_parameters(issue["fix"])
                }
            else:
                action["missing_capability"] = "render_control"

        return action

    def _create_action_from_improvement(
        self,
        improvement: Dict[str, Any],
        capabilities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Convert an improvement suggestion into an executable action."""

        action = {
            "type": "improvement",
            "priority": "medium",
            "description": improvement["improvement"],
            "can_execute": False,
            "implementation": {},
            "expected_impact": self._parse_impact(improvement.get("impact", "medium"))
        }

        # Similar parsing logic as issues but for improvements
        impl_text = improvement.get("implementation", "").lower()

        if "light" in impl_text:
            if "lighting" in capabilities:
                action["can_execute"] = True
                action["implementation"] = {
                    "system": "blender",
                    "component": "lighting",
                    "operation": "add_light" if "add" in impl_text else "adjust_light",
                    "parameters": self._extract_light_parameters(improvement.get("implementation", ""))
                }

        return action

    def _extract_light_parameters(self, text: str) -> Dict[str, Any]:
        """Extract lighting parameters from text description."""
        params = {}

        # Simple keyword extraction
        text_lower = text.lower()

        # Extract intensity values
        import re
        intensity_match = re.search(r'intensity[:\s]+(\d+\.?\d*)', text_lower)
        if intensity_match:
            params["intensity"] = float(intensity_match.group(1))

        # Extract light type
        if "sun" in text_lower:
            params["type"] = "SUN"
        elif "area" in text_lower:
            params["type"] = "AREA"
        elif "point" in text_lower:
            params["type"] = "POINT"
        elif "spot" in text_lower:
            params["type"] = "SPOT"

        # Extract position hints
        if "behind" in text_lower:
            params["position_hint"] = "behind_subject"
        elif "above" in text_lower:
            params["position_hint"] = "above_subject"
        elif "front" in text_lower:
            params["position_hint"] = "front_subject"

        return params

    def _extract_material_parameters(self, text: str) -> Dict[str, Any]:
        """Extract material parameters from text description."""
        params = {}
        import re

        text_lower = text.lower()

        # Extract roughness
        roughness_match = re.search(r'roughness[:\s]+(\d+\.?\d*)', text_lower)
        if roughness_match:
            params["roughness"] = float(roughness_match.group(1))

        # Extract metallic
        metallic_match = re.search(r'metallic[:\s]+(\d+\.?\d*)', text_lower)
        if metallic_match:
            params["metallic"] = float(metallic_match.group(1))

        return params

    def _extract_camera_parameters(self, text: str) -> Dict[str, Any]:
        """Extract camera parameters from text description."""
        params = {}
        import re

        text_lower = text.lower()

        # Extract angle changes
        angle_match = re.search(r'(\d+)°', text_lower)
        if angle_match:
            params["angle_change"] = int(angle_match.group(1))

        # Extract direction
        if "higher" in text_lower or "above" in text_lower:
            params["direction"] = "raise"
        elif "lower" in text_lower or "below" in text_lower:
            params["direction"] = "lower"
        elif "closer" in text_lower:
            params["direction"] = "zoom_in"
        elif "further" in text_lower or "back" in text_lower:
            params["direction"] = "zoom_out"

        return params

    def _extract_render_parameters(self, text: str) -> Dict[str, Any]:
        """Extract render parameters from text description."""
        params = {}
        import re

        text_lower = text.lower()

        # Extract sample count
        samples_match = re.search(r'(\d+)\s*samples?', text_lower)
        if samples_match:
            params["samples"] = int(samples_match.group(1))

        # Denoise
        if "denoise" in text_lower:
            params["denoise"] = "enable" in text_lower or "add" in text_lower

        return params

    def _parse_impact(self, impact_text: str) -> float:
        """Convert impact description to numeric value."""
        impact_text = impact_text.lower()
        if "high" in impact_text:
            return 0.15
        elif "medium" in impact_text:
            return 0.08
        elif "low" in impact_text:
            return 0.03
        return 0.05

    def _calculate_confidence(self, actions: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the action plan."""
        if not actions:
            return 0.0

        # Confidence based on:
        # - Number of executable actions
        # - Priority of actions
        # - Clarity of parameters

        executable = sum(1 for a in actions if a.get("can_execute", False))
        confidence = executable / len(actions)

        # Boost if we have critical fixes
        has_critical = any(a.get("priority") == "critical" for a in actions)
        if has_critical:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_system_enhancement_summary(self) -> Dict[str, Any]:
        """Get summary of all system enhancements requested across iterations."""
        summary = {
            "total_requests": len(self.system_enhancement_requests),
            "by_priority": {
                "high": [],
                "medium": [],
                "low": []
            },
            "missing_capabilities": set()
        }

        for req in self.system_enhancement_requests:
            priority = req.get("priority", "medium")
            summary["by_priority"][priority].append(req)
            summary["missing_capabilities"].add(req.get("missing_capability", "unknown"))

        summary["missing_capabilities"] = list(summary["missing_capabilities"])
        return summary

    def save_planning_history(self, filepath: str) -> None:
        """Save planning history to file."""
        with open(filepath, 'w') as f:
            json.dump({
                "total_plans": len(self.planning_history),
                "plans": self.planning_history,
                "system_enhancements": self.system_enhancement_requests
            }, f, indent=2)
