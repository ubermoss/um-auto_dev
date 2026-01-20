"""Token guard helpers for safe operation execution."""

from typing import Dict, Any

# Handle both package import and direct script execution
try:
    from .token_tracker import TokenTracker
except ImportError:
    from token_tracker import TokenTracker


class TokenGuard:
    """
    Helper for Claude Code to check token safety before operations.

    Provides warnings but doesn't block - human decides.
    """

    def __init__(self):
        """Initialize guard with tracker."""
        self.tracker = TokenTracker()

    def check_before_operation(
        self,
        current_tokens: int,
        operation_type: str,
        operation_description: str = None
    ) -> Dict[str, Any]:
        """
        Check if operation is safe to run.

        Args:
            current_tokens: Current token usage from system warnings
            operation_type: Type of operation (spawn_agent, iteration, etc.)
            operation_description: Human-readable description

        Returns:
            Safety check with recommendations
        """
        if operation_description is None:
            operation_description = operation_type.replace('_', ' ')

        # Get status and affordability
        status = self.tracker.check_status(current_tokens, operation_description)
        afford = self.tracker.can_afford(current_tokens, operation_type)
        estimate = self.tracker.estimate_operation_cost(operation_type)

        result = {
            "safe": True,
            "warning_level": status["level"],
            "can_afford": afford["can_afford"],
            "should_ask": False,
            "message": None,
            "user_prompt": None,
            "details": {
                "current": current_tokens,
                "remaining": status["remaining"],
                "estimate": estimate,
                "needed": afford["needed"]
            }
        }

        # Determine if we should ask user
        if status["level"] == "critical":
            result["safe"] = False
            result["should_ask"] = True
            result["message"] = f"⚠️ CRITICAL token level"
            result["user_prompt"] = self._format_critical_prompt(
                status, afford, operation_description, estimate
            )

        elif status["level"] == "checkpoint" and not afford["can_afford"]:
            result["should_ask"] = True
            result["message"] = f"🟡 Low tokens, operation may not complete"
            result["user_prompt"] = self._format_warning_prompt(
                status, afford, operation_description, estimate
            )

        elif status["level"] == "checkpoint":
            result["should_ask"] = True
            result["message"] = f"🟡 Checkpoint recommended before proceeding"
            result["user_prompt"] = self._format_checkpoint_prompt(
                status, afford, operation_description, estimate
            )

        return result

    def _format_critical_prompt(
        self,
        status: Dict,
        afford: Dict,
        operation: str,
        estimate: Dict
    ) -> str:
        """Format prompt for critical token level."""
        return f"""⚠️ **CRITICAL TOKEN LEVEL**

Current: {status['remaining']:,} tokens remaining ({status['usage_percent']:.1%} used)

You asked me to: {operation}
Estimated cost: {estimate.get('avg', estimate['max']):,} tokens ({estimate['source']})

**Risk:** Very likely to run out mid-operation.

**Options:**
- **Stop now** - Save state, resume in new session
- **Proceed anyway** - Accept risk of incomplete operation
- **Adjust** - Do something smaller/faster

Should I proceed with {operation}? [Stop/Proceed/Adjust]"""

    def _format_warning_prompt(
        self,
        status: Dict,
        afford: Dict,
        operation: str,
        estimate: Dict
    ) -> str:
        """Format prompt for warning level."""
        return f"""🟡 **LOW TOKEN WARNING**

Current: {status['remaining']:,} tokens remaining

You asked me to: {operation}
Estimated cost: {estimate.get('avg', estimate['max']):,} tokens ({estimate['source']})
Safety margin: {afford['safety_margin']:,} tokens

**Risk:** May not complete fully. Recommend checkpoint first.

**Suggestion:** Let me save current state, then proceed?

Continue with {operation}? [Yes/Checkpoint first/Cancel]"""

    def _format_checkpoint_prompt(
        self,
        status: Dict,
        afford: Dict,
        operation: str,
        estimate: Dict
    ) -> str:
        """Format prompt for checkpoint recommendation."""
        return f"""🟡 **CHECKPOINT RECOMMENDED**

Current: {status['remaining']:,} tokens remaining

You asked me to: {operation}
Estimated cost: ~{estimate.get('avg', estimate['max']):,} tokens ({estimate['source']})

This should fit, but we're at checkpoint threshold ({status['usage_percent']:.1%}).

**Options:**
- **Proceed** - Should be safe
- **Checkpoint first** - Extra safety
- **Defer** - Handle in next session

How would you like to proceed? [Proceed/Checkpoint/Defer]"""


def format_token_status_for_user(current_tokens: int) -> str:
    """
    Format current token status for display to user.

    Claude Code can call this to show token status.
    """
    tracker = TokenTracker()
    status = tracker.check_status(current_tokens)

    level_emoji = {
        "ok": "✓",
        "warning": "⚠️",
        "checkpoint": "🟡",
        "critical": "🚨"
    }

    emoji = level_emoji.get(status["level"], "•")

    return f"""{emoji} **Token Status:** {status['remaining']:,} / 200K remaining ({status['usage_percent']:.0%} used)"""


if __name__ == "__main__":
    """Test token guard."""
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    guard = TokenGuard()

    # Test scenarios
    scenarios = [
        (50000, "spawn_agent", "Spawn art director agent"),
        (165000, "iteration", "Run full iteration cycle"),
        (185000, "spawn_agent", "Spawn project analyst"),
    ]

    for tokens, op_type, op_desc in scenarios:
        print(f"\n{'='*70}")
        print(f"Scenario: {tokens:,} tokens used, want to: {op_desc}")
        print('='*70)

        result = guard.check_before_operation(tokens, op_type, op_desc)

        if result["should_ask"]:
            print(result["user_prompt"])
        else:
            print(f"✓ Safe to proceed")
            print(f"  {result['details']['remaining']:,} tokens remaining")
            print(f"  ~{result['details']['estimate'].get('avg', result['details']['estimate']['max']):,} tokens needed")
