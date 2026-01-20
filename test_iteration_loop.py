"""Quick test of the iteration loop with simulated evaluation."""

import sys
import io
from pathlib import Path

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from meta_framework.iteration_loop.coordinator import IterationCoordinator


def main():
    """Test the iteration loop with car render project."""

    project_path = Path(__file__).parent / "test_projects" / "car_room_render"
    scene_file = project_path / "assets" / "main.blend"

    # Check if scene file exists
    if not scene_file.exists():
        print(f"❌ Scene file not found: {scene_file}")
        print("Make sure the car assets are in test_projects/car_room_render/assets/")
        return 1

    # Initialize coordinator
    coordinator = IterationCoordinator(
        project_path=str(project_path),
        control_system="blender",
        max_iterations=3  # Start with just 3 iterations
    )

    # Define the goal
    goal = """Create a visually appealing render of the Ford Capri:
- Car should be well-lit and clearly visible
- Professional automotive photography style
- Dramatic but not over-the-top
- Clean, focused composition"""

    # Run the iteration loop
    results = coordinator.run_iteration_loop(
        goal_description=goal,
        initial_scene_path=str(scene_file),
        reference_image_path=None
    )

    # Display summary
    print("\n" + "=" * 70)
    print("🎉 ITERATION LOOP COMPLETE")
    print("=" * 70)

    summary = results["final_recommendation"]["summary"]
    print(f"\nTotal Iterations: {summary['total_iterations']}")
    print(f"Initial Score: {summary['initial_score']:.2f}")
    print(f"Final Score: {summary['final_score']:.2f}")
    print(f"Improvement: +{summary['improvement']:.2f} ({summary['improvement']*100:.0f}%)")
    print(f"Goal Achieved: {'✓ Yes' if summary['goal_achieved'] else '✗ Not yet'}")

    decisions = results["final_recommendation"]["decisions_made"]
    if decisions:
        print(f"\n📋 Decisions Made ({len(decisions)}):")
        for decision in decisions:
            print(f"  Iteration {decision['iteration']}: {decision['action']}")
            print(f"    → {decision['reason']}")

    enhancements = results["final_recommendation"]["system_enhancements"]
    if enhancements:
        print(f"\n🔧 System Enhancements Needed ({len(enhancements)}):")
        for enhancement in enhancements:
            print(f"  - {enhancement['missing_capability']}")
            print(f"    Reason: {enhancement['reason']}")

    questions = results["final_recommendation"]["questions_for_human"]
    if questions:
        print(f"\n❓ Questions for Human ({len(questions)}):")
        for question in questions:
            print(f"  - {question['question']}")

    next_steps = results["final_recommendation"]["next_steps"]
    if next_steps:
        print(f"\n👉 Next Steps:")
        for step in next_steps:
            print(f"  - {step}")

    print(f"\n📁 Session data saved to:")
    print(f"   {project_path}/iterations/{results['session_id']}/")

    print("\n" + "=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
