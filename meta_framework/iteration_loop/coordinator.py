"""Iteration Loop Coordinator - Orchestrates the eval→plan→execute cycle."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Add meta_framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluator.visual_evaluator import VisualEvaluator
from agents.planner.action_planner import ActionPlanner


class IterationCoordinator:
    """
    Coordinates the autonomous iteration loop.

    This is the "brain" that orchestrates:
    1. Render
    2. Evaluate
    3. Plan actions
    4. Execute actions
    5. Repeat or stop for human review
    """

    def __init__(
        self,
        project_path: str,
        control_system: str = "blender",
        max_iterations: int = 3
    ):
        """
        Initialize the coordinator.

        Args:
            project_path: Path to the test project
            control_system: Which control system to use (blender, unity, etc.)
            max_iterations: Maximum iterations before human review
        """
        self.project_path = Path(project_path)
        self.control_system = control_system
        self.max_iterations = max_iterations

        # Initialize agents
        self.evaluator = VisualEvaluator()
        self.planner = ActionPlanner()

        # State tracking
        self.current_iteration = 0
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.iterations_dir = self.project_path / "iterations" / self.session_id
        self.iterations_dir.mkdir(parents=True, exist_ok=True)

        # Load control system capabilities
        self.capabilities = self._load_capabilities()

    def _load_capabilities(self) -> Dict[str, list]:
        """Load what the current control system can do."""
        # This would be loaded from control_systems/{system}/capabilities.json
        # For MVP, hardcode basic Blender capabilities

        return {
            "lighting": [
                "adjust_intensity",
                "add_light",
                "remove_light",
                "change_color",
                "change_type"
            ],
            "camera": [
                "adjust_position",
                "adjust_rotation",
                "change_focal_length",
                "adjust_dof"
            ],
            "materials": [
                "adjust_roughness",
                "adjust_metallic",
                "adjust_color",
                "add_material"
            ],
            "render_settings": [
                "adjust_samples",
                "enable_denoise",
                "change_resolution",
                "change_engine"
            ],
            "objects": [
                "add_object",
                "transform_object",
                "duplicate_object"
            ]
        }

    def run_iteration_loop(
        self,
        goal_description: str,
        initial_scene_path: str,
        reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete iteration loop.

        Args:
            goal_description: What should the final render achieve?
            initial_scene_path: Path to starting .blend file
            reference_image_path: Optional reference image

        Returns:
            Session results including all iterations and final recommendation
        """
        print("=" * 70)
        print(f"🎬 Starting Iteration Loop - Session {self.session_id}")
        print("=" * 70)
        print(f"Goal: {goal_description}")
        print(f"Max Iterations: {self.max_iterations}")
        print()

        session_results = {
            "session_id": self.session_id,
            "goal": goal_description,
            "initial_scene": initial_scene_path,
            "reference_image": reference_image_path,
            "max_iterations": self.max_iterations,
            "iterations": [],
            "final_recommendation": None,
            "system_enhancements_made": [],
            "status": "running"
        }

        # Main iteration loop
        for iteration in range(1, self.max_iterations + 1):
            self.current_iteration = iteration

            print(f"\n{'─' * 70}")
            print(f"📍 Iteration {iteration}/{self.max_iterations}")
            print(f"{'─' * 70}")

            # Step 1: Render current state
            print(f"\n[1/4] 🎨 Rendering...")
            render_result = self._render_scene(initial_scene_path, iteration)

            if not render_result["success"]:
                print(f"❌ Render failed: {render_result.get('error')}")
                session_results["status"] = "failed"
                session_results["error"] = render_result.get("error")
                break

            print(f"✓ Render complete: {render_result['output_path']}")

            # Step 2: Evaluate the render
            print(f"\n[2/4] 🔍 Evaluating...")
            evaluation = self.evaluator.evaluate_render(
                image_path=render_result["output_path"],
                goal_description=goal_description,
                reference_image_path=reference_image_path,
                iteration_number=iteration,
                previous_feedback=session_results["iterations"]
            )

            # For MVP, since we don't have vision API yet, simulate scoring
            evaluation["analysis"] = self._simulate_evaluation(iteration)

            score = evaluation["analysis"]["overall_score"]
            print(f"✓ Evaluation complete - Score: {score:.2f}/1.0")

            # Step 3: Plan actions
            print(f"\n[3/4] 🧠 Planning actions...")
            plan = self.planner.plan_actions(evaluation, self.capabilities)

            print(f"✓ Plan created: {len(plan['actions'])} actions")
            for idx, action in enumerate(plan["actions"], 1):
                priority = action.get("priority", "medium")
                emoji = "🔴" if priority == "critical" else "🟡"
                print(f"  {emoji} {idx}. {action.get('issue', action.get('description', 'Action'))}")

            # Check if system enhancements needed
            if plan["system_enhancements_needed"]:
                print(f"\n⚠️  System enhancements needed:")
                for enhancement in plan["system_enhancements_needed"]:
                    print(f"  - {enhancement['missing_capability']}: {enhancement['reason']}")
                session_results["system_enhancements_made"].extend(
                    plan["system_enhancements_needed"]
                )

            # Step 4: Execute actions
            print(f"\n[4/4] ⚙️  Executing actions...")
            execution_results = self._execute_actions(plan["actions"], initial_scene_path)

            executed_count = sum(1 for r in execution_results if r.get("success", False))
            print(f"✓ Executed {executed_count}/{len(plan['actions'])} actions")

            # Save iteration data
            iteration_data = {
                "iteration": iteration,
                "render": render_result,
                "evaluation": evaluation,
                "plan": plan,
                "execution": execution_results
            }
            session_results["iterations"].append(iteration_data)
            self._save_iteration_data(iteration_data)

            # Check if we should stop
            stop_decision = self.evaluator.should_stop_iterating(
                evaluation,
                self.max_iterations
            )

            if stop_decision["should_stop"]:
                print(f"\n🛑 Stopping iteration: {stop_decision['reason']}")
                session_results["stop_reason"] = stop_decision["reason"]
                break

            # Progress summary
            print(f"\n📊 Iteration {iteration} Summary:")
            print(f"  Score: {score:.2f}")
            print(f"  Estimated impact: +{plan['estimated_impact']:.2f}")
            print(f"  Confidence: {plan['confidence']:.2f}")

        # Generate final recommendation
        print(f"\n{'=' * 70}")
        print("📋 Generating Human Review Package...")
        print(f"{'=' * 70}")

        session_results["final_recommendation"] = self._generate_recommendation(
            session_results
        )
        session_results["status"] = "completed"

        # Save session results
        session_file = self.iterations_dir / "session_results.json"
        with open(session_file, 'w') as f:
            json.dump(session_results, f, indent=2)

        print(f"\n✓ Session complete: {session_file}")
        print(f"✓ Total iterations: {len(session_results['iterations'])}")

        return session_results

    def _render_scene(self, scene_path: str, iteration: int) -> Dict[str, Any]:
        """
        Render the current scene state.

        Args:
            scene_path: Path to .blend file
            iteration: Current iteration number

        Returns:
            Render result with output path
        """
        # This would use the control system's render capabilities
        # For MVP, simulate render
        output_path = self.iterations_dir / f"render_iter_{iteration:03d}.png"

        # TODO: Implement actual rendering via BlenderExecutor
        # For now, return simulated success
        return {
            "success": True,
            "output_path": str(output_path),
            "render_time": 0.0,
            "samples": 128
        }

    def _simulate_evaluation(self, iteration: int) -> Dict[str, Any]:
        """Simulate evaluation for MVP (until vision API integrated)."""
        # Simulate progressive improvement
        base_score = 0.5 + (iteration * 0.1)

        return {
            "overall_score": min(base_score, 0.9),
            "technical_quality": {
                "lighting": {"score": 5 + iteration, "notes": "Improving"},
                "materials": {"score": 7, "notes": "Acceptable"},
                "composition": {"score": 8, "notes": "Good"},
                "focus": {"score": 7, "notes": "Sharp"},
                "render_quality": {"score": 9, "notes": "Clean"}
            },
            "artistic_quality": {
                "visual_appeal": {"score": 5 + iteration, "notes": "Getting better"},
                "mood": {"score": 5, "notes": "Neutral"},
                "style": {"score": 7, "notes": "Consistent"},
                "color_grading": {"score": 6, "notes": "Could improve"}
            },
            "goal_alignment": {
                "score": 5 + iteration,
                "meets_goal": base_score >= 0.8,
                "missing": ["Better lighting"] if iteration < 2 else [],
                "exceeds": []
            },
            "critical_issues": [
                {
                    "issue": "Scene too dark",
                    "why": "Subject barely visible",
                    "fix": "Increase key light intensity to 3.5",
                    "priority": "high"
                }
            ] if iteration == 1 else [],
            "improvements": [
                {
                    "improvement": "Add rim lighting",
                    "impact": "High",
                    "effort": "Low",
                    "implementation": "Add area light behind car, intensity 2.0"
                }
            ] if iteration == 2 else [],
            "questions_for_human": [],
            "confidence": 0.8,
            "reasoning": f"Iteration {iteration} analysis"
        }

    def _execute_actions(
        self,
        actions: List[Dict[str, Any]],
        scene_path: str
    ) -> List[Dict[str, Any]]:
        """
        Execute the planned actions.

        Args:
            actions: List of actions from planner
            scene_path: Path to scene file

        Returns:
            Execution results for each action
        """
        results = []

        for action in actions:
            if not action.get("can_execute", False):
                results.append({
                    "action": action,
                    "success": False,
                    "reason": "Cannot execute - missing capability"
                })
                continue

            # TODO: Implement actual execution via control system
            # For MVP, simulate execution
            results.append({
                "action": action,
                "success": True,
                "changes_made": action.get("implementation", {})
            })

        return results

    def _generate_recommendation(
        self,
        session_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human review package."""
        iterations = session_results["iterations"]
        total_iterations = len(iterations)

        if not iterations:
            return {"error": "No iterations completed"}

        first_score = iterations[0]["evaluation"]["analysis"]["overall_score"]
        last_score = iterations[-1]["evaluation"]["analysis"]["overall_score"]
        improvement = last_score - first_score

        recommendation = {
            "summary": {
                "total_iterations": total_iterations,
                "initial_score": first_score,
                "final_score": last_score,
                "improvement": improvement,
                "goal_achieved": last_score >= 0.85
            },
            "decisions_made": [],
            "system_enhancements": session_results["system_enhancements_made"],
            "questions_for_human": [],
            "next_steps": []
        }

        # Collect all decisions
        for iter_data in iterations:
            plan = iter_data.get("plan", {})
            for action in plan.get("actions", []):
                if action.get("can_execute"):
                    recommendation["decisions_made"].append({
                        "iteration": iter_data["iteration"],
                        "action": action.get("issue", action.get("description")),
                        "reason": action.get("fix", ""),
                        "impact": action.get("expected_impact", 0)
                    })

        # Collect questions
        for iter_data in iterations:
            eval_data = iter_data.get("evaluation", {})
            questions = eval_data.get("analysis", {}).get("questions_for_human", [])
            recommendation["questions_for_human"].extend(questions)

        # Suggest next steps
        if last_score < 0.85:
            recommendation["next_steps"].append(
                "Continue iterations - goal not yet achieved"
            )
        if recommendation["system_enhancements"]:
            recommendation["next_steps"].append(
                f"Implement {len(recommendation['system_enhancements'])} system enhancements"
            )
        if recommendation["questions_for_human"]:
            recommendation["next_steps"].append(
                "Answer accumulated questions to unblock progress"
            )

        return recommendation

    def _save_iteration_data(self, iteration_data: Dict[str, Any]) -> None:
        """Save individual iteration data."""
        iteration_num = iteration_data["iteration"]
        filepath = self.iterations_dir / f"iteration_{iteration_num:03d}.json"

        with open(filepath, 'w') as f:
            json.dump(iteration_data, f, indent=2)
