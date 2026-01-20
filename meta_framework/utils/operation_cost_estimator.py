"""Operation cost estimator for meta-meta, meta, and project layers.

This handles the token overhead of:
1. Meta-meta: Framework development (refactoring, new tools, architecture changes)
2. Meta: System execution (iteration loops, agent spawning)
3. Project: Target operations (Blender renders, file operations)

The meta-meta layer is the blind spot - we're developing the system that tracks tokens,
so we need rough estimates for framework development work.
"""

import sys
import io
from typing import Dict, Any, List, Optional
from pathlib import Path

# UTF-8 console fix for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Handle both package import and direct script execution
try:
    from .token_tracker import TokenTracker
except ImportError:
    from token_tracker import TokenTracker


class OperationCostEstimator:
    """
    Estimates token costs across all three layers of the system.

    Layers:
    - Meta-meta: Framework development (high cost, unknown)
    - Meta: Iteration execution (medium cost, learned)
    - Project: Target operations (low cost, deterministic)
    """

    def __init__(self):
        """Initialize with token tracker for meta layer."""
        self.tracker = TokenTracker()

        # Meta-meta layer estimates (framework development)
        # These are rough guesses based on typical Claude Code operations
        self.framework_ops = {
            "read_file": {"min": 200, "max": 500, "per_kb": 100},
            "edit_file": {"min": 500, "max": 2000, "per_kb": 200},
            "write_file": {"min": 800, "max": 3000, "per_kb": 300},
            "refactor_module": {"min": 3000, "max": 10000},
            "create_new_tool": {"min": 5000, "max": 15000},
            "test_integration": {"min": 2000, "max": 5000},
            "git_operations": {"min": 300, "max": 1000},
            "research_web": {"min": 2000, "max": 8000},
            "architecture_design": {"min": 4000, "max": 12000},
            "documentation": {"min": 1000, "max": 4000},
        }

        # Project layer estimates (cheap operations)
        self.project_ops = {
            "blender_render": {"cost": 100},  # Just subprocess call
            "read_image": {"cost": 500},  # Vision API overhead
            "file_io": {"cost": 50},
        }

    def estimate_framework_operation(
        self,
        operation: str,
        file_size_kb: Optional[int] = None,
        complexity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Estimate cost for framework development operations (meta-meta layer).

        Args:
            operation: Type of framework operation
            file_size_kb: File size for file operations
            complexity: low/medium/high for operations that scale

        Returns:
            Estimate with min/max/explanation
        """
        if operation not in self.framework_ops:
            # Unknown operation - use conservative estimate
            return {
                "operation": operation,
                "min": 1000,
                "max": 5000,
                "avg": 3000,
                "source": "fallback",
                "explanation": "Unknown framework operation - conservative estimate"
            }

        base = self.framework_ops[operation].copy()

        # Scale by file size if applicable
        if file_size_kb and "per_kb" in base:
            per_kb = base["per_kb"]
            size_cost = file_size_kb * per_kb
            base["min"] += size_cost
            base["max"] += size_cost

        # Scale by complexity
        complexity_multiplier = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.5
        }.get(complexity, 1.0)

        base["min"] = int(base["min"] * complexity_multiplier)
        base["max"] = int(base["max"] * complexity_multiplier)
        base["avg"] = (base["min"] + base["max"]) // 2
        base["source"] = "framework_estimate"
        base["operation"] = operation

        return base

    def estimate_composite_operation(
        self,
        description: str,
        affected_files: List[str] = None,
        includes_research: bool = False,
        includes_testing: bool = False
    ) -> Dict[str, Any]:
        """
        Estimate complex operations that span multiple sub-operations.

        Examples:
        - "Refactor all code" = multiple edits + testing
        - "Add new capability" = research + write + test + document
        - "Fix bug" = read + edit + test

        Args:
            description: Human-readable operation description
            affected_files: List of file paths that will be modified
            includes_research: Whether this needs web research
            includes_testing: Whether this includes testing/validation

        Returns:
            Composite estimate with breakdown
        """
        breakdown = []
        total_min = 0
        total_max = 0

        # Research component
        if includes_research:
            research = self.estimate_framework_operation("research_web")
            breakdown.append(("Research/WebSearch", research))
            total_min += research["min"]
            total_max += research["max"]

        # File operations
        if affected_files:
            for file_path in affected_files:
                path = Path(file_path)
                if path.exists():
                    size_kb = path.stat().st_size // 1024
                    # Assume editing existing files
                    edit = self.estimate_framework_operation("edit_file", size_kb)
                    breakdown.append((f"Edit {path.name}", edit))
                    total_min += edit["min"]
                    total_max += edit["max"]
                else:
                    # New file
                    write = self.estimate_framework_operation("write_file")
                    breakdown.append((f"Create {path.name}", write))
                    total_min += write["min"]
                    total_max += write["max"]
        else:
            # No specific files - use heuristic based on description
            if "refactor all" in description.lower():
                # Assume 5-10 files affected
                refactor = self.estimate_framework_operation("refactor_module", complexity="high")
                breakdown.append(("Refactor multiple files", refactor))
                total_min += refactor["min"] * 3
                total_max += refactor["max"] * 5
            elif "new tool" in description.lower() or "create" in description.lower():
                create = self.estimate_framework_operation("create_new_tool")
                breakdown.append(("Create new tool", create))
                total_min += create["min"]
                total_max += create["max"]
            else:
                # Generic operation
                edit = self.estimate_framework_operation("edit_file", complexity="medium")
                breakdown.append(("Generic edit", edit))
                total_min += edit["min"]
                total_max += edit["max"]

        # Testing component
        if includes_testing:
            test = self.estimate_framework_operation("test_integration")
            breakdown.append(("Test/validate", test))
            total_min += test["min"]
            total_max += test["max"]

        # Git operations (always included)
        git = self.estimate_framework_operation("git_operations")
        breakdown.append(("Git commit", git))
        total_min += git["min"]
        total_max += git["max"]

        return {
            "description": description,
            "total_min": total_min,
            "total_max": total_max,
            "total_avg": (total_min + total_max) // 2,
            "breakdown": breakdown,
            "source": "composite"
        }

    def check_operation_feasibility(
        self,
        current_tokens: int,
        operation_description: str,
        affected_files: List[str] = None,
        includes_research: bool = False,
        includes_testing: bool = False,
        layer: str = "meta-meta"
    ) -> Dict[str, Any]:
        """
        Check if an operation is feasible given current token usage.

        Args:
            current_tokens: Current token count
            operation_description: What you want to do
            affected_files: Files that will be modified
            includes_research: Whether research is needed
            includes_testing: Whether testing is needed
            layer: Which layer (meta-meta, meta, project)

        Returns:
            Feasibility check with recommendation
        """
        remaining = 200000 - current_tokens
        usage_percent = current_tokens / 200000

        # Get estimate based on layer
        if layer == "meta-meta":
            estimate = self.estimate_composite_operation(
                operation_description,
                affected_files,
                includes_research,
                includes_testing
            )
            estimated_cost = estimate["total_max"]  # Use max for safety
        elif layer == "meta":
            # Use learned estimates from tracker
            op_type = "iteration"  # Default
            if "spawn" in operation_description.lower():
                op_type = "spawn_agent"
            learned = self.tracker.estimate_operation_cost(op_type)
            estimated_cost = learned.get("max", learned.get("avg", 5000))
            estimate = {
                "description": operation_description,
                "total_max": estimated_cost,
                "source": "learned"
            }
        else:  # project layer
            estimated_cost = 500  # Project operations are cheap
            estimate = {
                "description": operation_description,
                "total_max": estimated_cost,
                "source": "project"
            }

        # Safety margin (10% of remaining)
        safety_margin = int(remaining * 0.1)
        needed = estimated_cost + safety_margin

        can_afford = remaining >= needed

        # Determine warning level
        if usage_percent >= 0.90:
            level = "critical"
            recommendation = "STOP - Save state and resume in new session"
        elif usage_percent >= 0.80:
            level = "checkpoint"
            recommendation = "Consider checkpointing before proceeding"
        elif not can_afford:
            level = "warning"
            recommendation = f"Insufficient tokens. Need ~{needed:,}, have {remaining:,}"
        else:
            level = "ok"
            recommendation = "Safe to proceed"

        return {
            "feasible": can_afford and level != "critical",
            "level": level,
            "current_tokens": current_tokens,
            "remaining": remaining,
            "usage_percent": usage_percent,
            "estimated_cost": estimated_cost,
            "safety_margin": safety_margin,
            "needed": needed,
            "estimate_details": estimate,
            "recommendation": recommendation,
            "layer": layer
        }

    def format_warning(self, check: Dict[str, Any]) -> str:
        """Format a user-friendly warning message."""
        level_emoji = {
            "ok": "✓",
            "warning": "⚠️",
            "checkpoint": "🟡",
            "critical": "🚨"
        }

        emoji = level_emoji.get(check["level"], "•")

        if check["level"] == "critical":
            return f"""{emoji} **CRITICAL TOKEN LEVEL**

Current: {check['remaining']:,} tokens remaining ({check['usage_percent']:.1%} used)

You asked me to: {check['estimate_details']['description']}
Layer: {check['layer']} (framework development overhead)
Estimated cost: ~{check['estimated_cost']:,} tokens

**Risk:** Very likely to run out mid-operation.

**Options:**
- **Stop now** - Save state, resume in new session (RECOMMENDED)
- **Proceed anyway** - Accept risk of incomplete work
- **Simplify** - Break into smaller operations

Should I proceed? [Stop/Proceed/Simplify]"""

        elif check["level"] == "checkpoint" or not check["feasible"]:
            return f"""{emoji} **TOKEN WARNING**

Current: {check['remaining']:,} tokens remaining ({check['usage_percent']:.1%} used)

You asked me to: {check['estimate_details']['description']}
Layer: {check['layer']}
Estimated cost: ~{check['estimated_cost']:,} tokens

**Recommendation:** {check['recommendation']}

Should I proceed? [Yes/Checkpoint first/Cancel]"""

        else:
            return f"{emoji} Safe to proceed: {check['remaining']:,} tokens remaining (~{check['estimated_cost']:,} needed)"


if __name__ == "__main__":
    """CLI and test interface for operation cost estimator."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Estimate token costs for operations")
    parser.add_argument("--current-tokens", type=int, help="Current token usage")
    parser.add_argument("--operation", type=str, help="Operation description")
    parser.add_argument("--layer", type=str, choices=["meta-meta", "meta", "project"], default="meta-meta")
    parser.add_argument("--files", nargs="*", help="Files affected by operation")
    parser.add_argument("--research", action="store_true", help="Includes web research")
    parser.add_argument("--testing", action="store_true", help="Includes testing")
    parser.add_argument("--json-output", action="store_true", help="Output as JSON")
    parser.add_argument("--test", action="store_true", help="Run test scenarios")

    args = parser.parse_args()

    estimator = OperationCostEstimator()

    # CLI mode
    if args.current_tokens and args.operation:
        check = estimator.check_operation_feasibility(
            args.current_tokens,
            args.operation,
            affected_files=args.files,
            includes_research=args.research,
            includes_testing=args.testing,
            layer=args.layer
        )

        if args.json_output:
            output = {
                "feasible": check["feasible"],
                "level": check["level"],
                "remaining": check["remaining"],
                "estimated_cost": check["estimated_cost"],
                "recommendation": check["recommendation"],
                "warning": estimator.format_warning(check) if check["level"] != "ok" else None
            }
            print(json.dumps(output, indent=2))
        else:
            print(estimator.format_warning(check))

            if check["estimate_details"].get("breakdown"):
                print("\nCost Breakdown:")
                for step, estimate in check["estimate_details"]["breakdown"]:
                    print(f"  • {step}: {estimate.get('min', 0):,}-{estimate.get('max', 0):,} tokens")
        exit(0)

    # Test mode (default if no CLI args)

    print("\n" + "="*70)
    print("META-META LAYER: Framework Development Operations")
    print("="*70)

    # Test framework operations
    scenarios = [
        ("Edit small file", 70000, "edit_file", ["token_guard.py"], False, False),
        ("Refactor all code", 160000, "refactor all code", None, False, True),
        ("Add new capability", 150000, "create new histogram analyzer", None, True, True),
        ("Fix critical bug", 185000, "fix unicode error", ["utils/token_tracker.py"], False, True),
    ]

    for desc, tokens, operation, files, research, testing in scenarios:
        print(f"\n{'─'*70}")
        print(f"Scenario: {desc} (at {tokens:,} tokens)")
        print('─'*70)

        check = estimator.check_operation_feasibility(
            tokens,
            operation,
            affected_files=files,
            includes_research=research,
            includes_testing=testing,
            layer="meta-meta"
        )

        print(estimator.format_warning(check))

        if check["estimate_details"].get("breakdown"):
            print("\nCost Breakdown:")
            for step, estimate in check["estimate_details"]["breakdown"]:
                print(f"  • {step}: {estimate.get('min', 0):,}-{estimate.get('max', 0):,} tokens")
