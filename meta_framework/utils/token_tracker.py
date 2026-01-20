"""Token tracking and smart checkpoint system."""

from typing import Optional, Dict, Any, List
import sys
import json
from pathlib import Path
from datetime import datetime


class TokenTracker:
    """
    Track token usage and suggest checkpoints.

    Note: Token counts are approximate based on Claude's system messages.
    Actual usage shown in <system_warning> tags.

    Learns from real usage to improve estimates over time.
    """

    def __init__(
        self,
        max_tokens: int = 200000,
        usage_log_path: str = None
    ):
        """Initialize tracker."""
        self.max_tokens = max_tokens
        self.warning_threshold = 0.75  # Warn at 75%
        self.critical_threshold = 0.90  # Critical at 90%
        self.checkpoint_threshold = 0.80  # Suggest checkpoint at 80%

        # Usage tracking for learning
        if usage_log_path is None:
            usage_log_path = Path(__file__).parent.parent / "data" / "token_usage.json"
        self.usage_log_path = Path(usage_log_path)
        self.usage_history = self._load_usage_history()

    def check_status(
        self,
        current_tokens: int,
        operation_name: str = "operation"
    ) -> Dict[str, Any]:
        """
        Check token status and provide recommendations.

        Args:
            current_tokens: Current token usage
            operation_name: What operation is being considered

        Returns:
            Status dict with recommendations
        """
        usage_percent = current_tokens / self.max_tokens
        remaining = self.max_tokens - current_tokens

        status = {
            "current": current_tokens,
            "max": self.max_tokens,
            "remaining": remaining,
            "usage_percent": usage_percent,
            "level": self._get_level(usage_percent),
            "should_checkpoint": usage_percent >= self.checkpoint_threshold,
            "should_stop": usage_percent >= self.critical_threshold,
            "message": self._get_message(usage_percent, remaining, operation_name)
        }

        return status

    def _get_level(self, usage_percent: float) -> str:
        """Get status level."""
        if usage_percent >= self.critical_threshold:
            return "critical"
        elif usage_percent >= self.checkpoint_threshold:
            return "checkpoint"
        elif usage_percent >= self.warning_threshold:
            return "warning"
        else:
            return "ok"

    def _get_message(
        self,
        usage_percent: float,
        remaining: int,
        operation: str
    ) -> str:
        """Generate status message."""
        if usage_percent >= self.critical_threshold:
            return f"⚠️ CRITICAL: {remaining} tokens left. Stop and save state NOW."

        elif usage_percent >= self.checkpoint_threshold:
            return f"🟡 CHECKPOINT: {remaining} tokens left. Save state before {operation}."

        elif usage_percent >= self.warning_threshold:
            return f"ℹ️ WARNING: {remaining} tokens remaining. Consider checkpointing soon."

        else:
            return f"✓ OK: {remaining} tokens remaining. Safe to continue."

    def _load_usage_history(self) -> Dict[str, List[int]]:
        """Load historical usage data."""
        if self.usage_log_path.exists():
            try:
                with open(self.usage_log_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_usage_history(self):
        """Save usage history to disk."""
        self.usage_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_log_path, 'w') as f:
            json.dump(self.usage_history, f, indent=2)

    def record_actual_usage(
        self,
        operation_type: str,
        tokens_before: int,
        tokens_after: int
    ):
        """
        Record actual token usage for an operation.

        This builds a history that improves estimates over time.

        Args:
            operation_type: Type of operation (spawn_agent, render, etc.)
            tokens_before: Token count before operation
            tokens_after: Token count after operation
        """
        actual_cost = tokens_after - tokens_before

        if operation_type not in self.usage_history:
            self.usage_history[operation_type] = []

        self.usage_history[operation_type].append({
            "cost": actual_cost,
            "timestamp": datetime.now().isoformat(),
            "tokens_before": tokens_before,
            "tokens_after": tokens_after
        })

        # Keep last 100 samples per operation
        if len(self.usage_history[operation_type]) > 100:
            self.usage_history[operation_type] = self.usage_history[operation_type][-100:]

        self._save_usage_history()

    def estimate_operation_cost(
        self,
        operation_type: str
    ) -> Dict[str, int]:
        """
        Estimate token cost for operation types.

        Uses learned data if available, falls back to defaults.

        Returns min and max estimates.
        """
        # Default estimates (baseline)
        defaults = {
            "spawn_agent": {"min": 2000, "max": 5000},
            "render": {"min": 500, "max": 1000},
            "evaluate_image": {"min": 1000, "max": 3000},
            "write_code": {"min": 1500, "max": 4000},
            "research": {"min": 2000, "max": 6000},
            "iteration": {"min": 5000, "max": 15000},
        }

        # If we have historical data, use it
        if operation_type in self.usage_history:
            history = self.usage_history[operation_type]
            if len(history) >= 3:  # Need at least 3 samples
                costs = [entry["cost"] for entry in history]
                learned_min = min(costs)
                learned_max = max(costs)
                learned_avg = sum(costs) // len(costs)

                # Use learned data with safety margin
                return {
                    "min": learned_min,
                    "max": learned_max,
                    "avg": learned_avg,
                    "samples": len(costs),
                    "source": "learned"
                }

        # Fall back to defaults
        estimate = defaults.get(operation_type, {"min": 1000, "max": 5000})
        estimate["source"] = "default"
        estimate["samples"] = 0
        return estimate

    def can_afford(
        self,
        current_tokens: int,
        operation_type: str,
        safety_margin: int = 5000
    ) -> Dict[str, Any]:
        """
        Check if we can afford an operation.

        Args:
            current_tokens: Current usage
            operation_type: Type of operation
            safety_margin: Extra tokens to keep as buffer

        Returns:
            Can afford check with details
        """
        estimate = self.estimate_operation_cost(operation_type)
        remaining = self.max_tokens - current_tokens

        # Use max estimate for safety
        needed = estimate["max"] + safety_margin
        can_do = remaining >= needed

        return {
            "can_afford": can_do,
            "remaining": remaining,
            "needed": needed,
            "estimate": estimate,
            "safety_margin": safety_margin,
            "recommendation": (
                "Safe to proceed" if can_do
                else f"Insufficient tokens. Need ~{needed}, have {remaining}. Checkpoint first."
            )
        }

    def format_status(self, status: Dict[str, Any]) -> str:
        """Format status for display."""
        level = status["level"]
        emoji = {
            "ok": "✓",
            "warning": "ℹ️",
            "checkpoint": "🟡",
            "critical": "⚠️"
        }.get(level, "•")

        return f"""
{emoji} Token Status: {level.upper()}
├─ Usage: {status['current']:,}/{status['max']:,} ({status['usage_percent']:.1%})
├─ Remaining: {status['remaining']:,}
└─ {status['message']}
"""

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learned usage patterns."""
        stats = {
            "operations_tracked": len(self.usage_history),
            "total_samples": sum(len(history) for history in self.usage_history.values()),
            "operation_stats": {}
        }

        for op_type, history in self.usage_history.items():
            if history:
                costs = [entry["cost"] for entry in history]
                stats["operation_stats"][op_type] = {
                    "samples": len(costs),
                    "min": min(costs),
                    "max": max(costs),
                    "avg": sum(costs) // len(costs),
                    "last_cost": costs[-1]
                }

        return stats


def get_current_token_usage() -> Optional[int]:
    """
    Try to extract current token usage from context.

    Note: This is a placeholder. In actual use, Claude Code
    can see token usage in system warnings.

    Returns None if can't determine.
    """
    # In real usage, Claude can read from system warnings
    # For now, return None to indicate manual tracking
    return None


if __name__ == "__main__":
    """Quick test of token tracker."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    tracker = TokenTracker()

    # Test at various levels
    test_levels = [
        (50000, "Early in session"),
        (140000, "Getting into warning zone"),
        (165000, "Checkpoint recommended"),
        (185000, "Critical - stop soon")
    ]

    for tokens, desc in test_levels:
        print(f"\n{'='*60}")
        print(desc)
        print('='*60)

        status = tracker.check_status(tokens, "next iteration")
        print(tracker.format_status(status))

        # Check if can afford an iteration
        afford = tracker.can_afford(tokens, "iteration")
        print(f"Can afford full iteration: {afford['can_afford']}")
        print(f"  {afford['recommendation']}")
