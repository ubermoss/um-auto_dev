"""Visual Evaluator Agent - Analyzes renders and provides actionable feedback."""

import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class VisualEvaluator:
    """
    Evaluates visual outputs and provides structured feedback.

    This agent acts as the "art director" - it looks at renders and identifies
    what's wrong, what's right, and what should be changed.
    """

    def __init__(self, model: str = "claude-sonnet-4.5"):
        """Initialize the evaluator with a vision model."""
        self.model = model
        self.evaluation_history: List[Dict[str, Any]] = []

    def evaluate_render(
        self,
        image_path: str,
        goal_description: str,
        reference_image_path: Optional[str] = None,
        iteration_number: int = 1,
        previous_feedback: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a render against the goal.

        Args:
            image_path: Path to the rendered image
            goal_description: What should this render achieve?
            reference_image_path: Optional reference image to match
            iteration_number: Current iteration number
            previous_feedback: Feedback from previous iterations

        Returns:
            Structured evaluation with scores, issues, and recommendations
        """
        evaluation = {
            "iteration": iteration_number,
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "goal": goal_description,
            "has_reference": reference_image_path is not None
        }

        # This is where we'd call Claude's vision API
        # For now, structure the evaluation format

        # Build the prompt for vision analysis
        prompt = self._build_evaluation_prompt(
            goal_description,
            iteration_number,
            previous_feedback
        )

        # TODO: Implement actual Claude vision API call
        # For MVP, we'll structure how this should work
        evaluation["prompt"] = prompt
        evaluation["analysis"] = {
            "overall_score": 0.0,  # 0-1 scale
            "technical_quality": {},
            "artistic_quality": {},
            "goal_alignment": {},
            "critical_issues": [],
            "improvements": [],
            "questions_for_human": []
        }

        self.evaluation_history.append(evaluation)
        return evaluation

    def _build_evaluation_prompt(
        self,
        goal: str,
        iteration: int,
        previous_feedback: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build the prompt for vision model evaluation."""

        prompt = f"""You are an expert art director evaluating a 3D render.

**Goal:** {goal}

**Iteration:** {iteration}

**Your Task:**
Analyze this render and provide structured, actionable feedback.

**Evaluate these aspects:**

1. **Technical Quality** (0-10 for each):
   - Lighting: Exposure, shadows, highlights
   - Materials: Realism, reflections, roughness
   - Composition: Framing, rule of thirds, balance
   - Focus: Depth of field, subject clarity
   - Render Quality: Noise, artifacts, resolution

2. **Artistic Quality** (0-10 for each):
   - Visual Appeal: Does it look good?
   - Mood: Does it convey the right feeling?
   - Style: Consistent, professional?
   - Color Grading: Harmonious, intentional?

3. **Goal Alignment** (0-10):
   - How well does this achieve the stated goal?
   - What's missing from the goal?
   - What's exceeding expectations?

**Critical Issues** (Must Fix):
List 1-3 issues that MUST be fixed for this to be acceptable.
For each issue:
- What's wrong (specific, measurable)
- Why it matters
- Suggested fix (actionable)

**Improvements** (Should Consider):
List 2-4 improvements that would elevate the quality.
For each:
- What could be better
- Expected impact
- Difficulty/effort estimate

**Questions for Human**:
If you encounter decisions you can't make autonomously:
- Style choices (photorealistic vs stylized)
- Subjective preferences (which angle looks better)
- Missing requirements (should there be props in background?)
"""

        if previous_feedback:
            prompt += f"""

**Previous Feedback Context:**
You previously identified these issues. Check if they were addressed:
"""
            for idx, prev in enumerate(previous_feedback[-3:], 1):  # Last 3 iterations
                if "critical_issues" in prev.get("analysis", {}):
                    prompt += f"\nIteration {prev['iteration']}:\n"
                    for issue in prev["analysis"]["critical_issues"]:
                        prompt += f"  - {issue}\n"

        prompt += """

**Output Format (JSON):**
```json
{
  "overall_score": 0.65,
  "technical_quality": {
    "lighting": {"score": 6, "notes": "Too dark, increase key light"},
    "materials": {"score": 7, "notes": "Car paint looks good"},
    "composition": {"score": 8, "notes": "Well framed"},
    "focus": {"score": 7, "notes": "Sharp focus on car"},
    "render_quality": {"score": 9, "notes": "Clean render"}
  },
  "artistic_quality": {
    "visual_appeal": {"score": 6, "notes": "Functional but bland"},
    "mood": {"score": 5, "notes": "Lacks atmosphere"},
    "style": {"score": 7, "notes": "Consistent style"},
    "color_grading": {"score": 6, "notes": "Could use warmth"}
  },
  "goal_alignment": {
    "score": 6,
    "meets_goal": false,
    "missing": ["Better lighting", "More dramatic angle"],
    "exceeds": ["Car detail is excellent"]
  },
  "critical_issues": [
    {
      "issue": "Scene too dark - car barely visible",
      "why": "Subject should be clearly visible",
      "fix": "Increase key light intensity to 3.0+",
      "priority": "high"
    }
  ],
  "improvements": [
    {
      "improvement": "Add rim lighting to separate car from background",
      "impact": "High - adds depth and professionalism",
      "effort": "Low - add single light",
      "implementation": "Add area light behind car, intensity 2.0"
    }
  ],
  "questions_for_human": [
    {
      "question": "Should the background be a plain wall or detailed environment?",
      "context": "Currently plain, but could add garage/showroom",
      "options": ["Keep simple", "Add environment", "Let me decide"]
    }
  ],
  "confidence": 0.85,
  "reasoning": "Clear technical issues identified. Scene needs better lighting first."
}
```

Be specific, measurable, and actionable. Every suggestion should be implementable.
"""
        return prompt

    def compare_iterations(
        self,
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple iterations to identify trends.

        Returns:
            Analysis of progress, regressions, and patterns
        """
        if len(evaluations) < 2:
            return {"message": "Need at least 2 iterations to compare"}

        comparison = {
            "iterations_analyzed": len(evaluations),
            "overall_trend": "improving",  # improving, declining, stagnant
            "score_progression": [],
            "recurring_issues": [],
            "resolved_issues": [],
            "new_issues": [],
            "recommendations": []
        }

        # Extract scores
        for eval_data in evaluations:
            if "analysis" in eval_data and "overall_score" in eval_data["analysis"]:
                comparison["score_progression"].append({
                    "iteration": eval_data["iteration"],
                    "score": eval_data["analysis"]["overall_score"]
                })

        # Determine trend
        if len(comparison["score_progression"]) >= 2:
            first_score = comparison["score_progression"][0]["score"]
            last_score = comparison["score_progression"][-1]["score"]

            if last_score > first_score + 0.1:
                comparison["overall_trend"] = "improving"
            elif last_score < first_score - 0.1:
                comparison["overall_trend"] = "declining"
            else:
                comparison["overall_trend"] = "stagnant"

        return comparison

    def should_stop_iterating(
        self,
        latest_evaluation: Dict[str, Any],
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Determine if we should stop iterating and involve human.

        Returns:
            Decision with reasoning
        """
        decision = {
            "should_stop": False,
            "reason": None,
            "confidence": 0.0
        }

        iteration = latest_evaluation.get("iteration", 0)

        # Check max iterations
        if iteration >= max_iterations:
            decision["should_stop"] = True
            decision["reason"] = f"Reached max iterations ({max_iterations})"
            decision["confidence"] = 1.0
            return decision

        # Check if goal is achieved
        analysis = latest_evaluation.get("analysis", {})
        overall_score = analysis.get("overall_score", 0)

        if overall_score >= 0.85:
            decision["should_stop"] = True
            decision["reason"] = "Goal achieved (score >= 0.85)"
            decision["confidence"] = 0.9
            return decision

        # Check if we have questions that need human input
        questions = analysis.get("questions_for_human", [])
        if len(questions) >= 2:
            decision["should_stop"] = True
            decision["reason"] = f"Accumulated {len(questions)} questions needing human input"
            decision["confidence"] = 0.8
            return decision

        # Check if we're stagnating
        if len(self.evaluation_history) >= 3:
            comparison = self.compare_iterations(self.evaluation_history[-3:])
            if comparison["overall_trend"] == "stagnant":
                decision["should_stop"] = True
                decision["reason"] = "No improvement in last 3 iterations"
                decision["confidence"] = 0.7
                return decision

        return decision

    def save_evaluation(self, filepath: str) -> None:
        """Save evaluation history to file."""
        with open(filepath, 'w') as f:
            json.dump({
                "model": self.model,
                "total_evaluations": len(self.evaluation_history),
                "evaluations": self.evaluation_history
            }, f, indent=2)

    def load_evaluation(self, filepath: str) -> None:
        """Load evaluation history from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.evaluation_history = data.get("evaluations", [])
