"""Test runner for the simple cube scenario."""

import sys
import json
from pathlib import Path
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from executor.executor import BlenderExecutor
from blender.blender_tools import BlenderTools
from state.state_manager import StateManager
from git.git_tools import GitTools


def run_simple_cube_scenario():
    """Execute the simple cube scenario."""
    print("=" * 60)
    print("Running Simple Cube Scenario")
    print("=" * 60)

    # Initialize components
    scenario_dir = Path(__file__).parent
    output_dir = scenario_dir / "output"
    state_file = output_dir / "scenario_state.json"

    executor = BlenderExecutor()
    blender_tools = BlenderTools()
    state = StateManager(str(state_file))
    git = GitTools(repo_path=scenario_dir.parent.parent)

    # Load scenario
    with open(scenario_dir / "scenario.json", 'r') as f:
        scenario = json.load(f)

    print(f"\nScenario: {scenario['name']}")
    print(f"Description: {scenario['description']}\n")

    # Initialize git if not already
    if not git.is_repo():
        print("Initializing git repository...")
        result = git.init_repo()
        if result["success"]:
            print("✓ Git repository initialized")
        else:
            print(f"✗ Failed to initialize git: {result['stderr']}")

    # Create a branch for this scenario
    branch_name = f"scenario-simple-cube-{state.state['conversation_id']}"
    print(f"\nCreating branch: {branch_name}")
    result = git.create_branch(branch_name)
    if result["success"]:
        print(f"✓ Branch '{branch_name}' created")
        state.set_current_branch(branch_name)
    else:
        # Branch might already exist, try to checkout
        result = git.checkout_branch(branch_name)
        if result["success"]:
            print(f"✓ Checked out existing branch '{branch_name}'")

    # Generate script for each step
    scripts = []

    for step in scenario["steps"]:
        print(f"\n[Step {step['id']}] {step['description']}")

        if step["type"] == "create_object":
            if step["object_type"] == "cube":
                script = blender_tools.generate_cube_script(
                    location=tuple(step["parameters"]["location"]),
                    scale=tuple(step["parameters"]["scale"]),
                    name=step["parameters"]["name"]
                )
                scripts.append(script)
                print("  → Generated cube creation script")

        elif step["type"] == "apply_material":
            script = blender_tools.generate_material_script(
                object_name=step["target_object"],
                color=tuple(step["parameters"]["color"]),
                material_name=step["parameters"]["material_name"]
            )
            scripts.append(script)
            print("  → Generated material script")

        elif step["type"] == "setup_camera":
            script = blender_tools.generate_camera_script(
                location=tuple(step["parameters"]["location"]),
                rotation=tuple(step["parameters"]["rotation"]),
                name=step["parameters"]["name"]
            )
            scripts.append(script)
            print("  → Generated camera setup script")

        elif step["type"] == "setup_light":
            script = blender_tools.generate_light_script(
                light_type=step["parameters"]["light_type"],
                location=tuple(step["parameters"]["location"]),
                energy=step["parameters"]["energy"],
                name=step["parameters"]["name"]
            )
            scripts.append(script)
            print("  → Generated light setup script")

        elif step["type"] == "configure_render":
            script = blender_tools.generate_render_settings_script(
                engine=step["parameters"]["engine"],
                samples=step["parameters"]["samples"],
                resolution_x=step["parameters"]["resolution_x"],
                resolution_y=step["parameters"]["resolution_y"]
            )
            scripts.append(script)
            print("  → Generated render configuration script")

        elif step["type"] == "save_file":
            output_path = Path(__file__).parent.parent.parent / step["parameters"]["output_path"]
            script = blender_tools.generate_save_script(str(output_path))
            scripts.append(script)
            print(f"  → Generated save script for: {output_path}")
            state.set_current_file(str(output_path))

    # Add scene info at the end
    scripts.append(blender_tools.generate_scene_info_script())

    # Combine all scripts
    combined_script = blender_tools.combine_scripts(scripts)

    # Save the generated script
    script_path = output_dir / "generated_scene.py"
    with open(script_path, 'w') as f:
        f.write(combined_script)
    print(f"\n✓ Combined script saved to: {script_path}")

    # Execute the script in Blender
    print("\n" + "=" * 60)
    print("Executing script in Blender...")
    print("=" * 60)

    result = executor.execute_script(
        script_path=str(script_path),
        background=True
    )

    # Record execution
    state.add_execution(
        command=f"execute_scenario:{scenario['name']}",
        result=result
    )

    # Display results
    print("\n" + "=" * 60)
    print("Execution Results")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Return Code: {result['returncode']}")

    if result['stdout']:
        print("\n--- Output ---")
        # Filter out Blender's verbose startup messages
        lines = result['stdout'].split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['created', 'configured', 'saved', 'Scene Information', '===', 'Objects']):
                print(line)

    if result['stderr'] and result['returncode'] != 0:
        print("\n--- Errors ---")
        print(result['stderr'])

    # Commit the results
    if result['success']:
        print("\n" + "=" * 60)
        print("Committing Results")
        print("=" * 60)

        # Add files to git
        files_to_add = [
            str(script_path.relative_to(git.repo_path)),
            str(state_file.relative_to(git.repo_path))
        ]

        blend_file = state.get_current_file()
        if blend_file and Path(blend_file).exists():
            files_to_add.append(str(Path(blend_file).relative_to(git.repo_path)))

        git_result = git.add_files(files_to_add)
        if git_result['success']:
            print(f"✓ Files staged for commit")

            commit_msg = f"Scenario: {scenario['name']}\n\nGenerated and executed simple cube scene with red material."
            git_result = git.commit(commit_msg)
            if git_result['success']:
                print(f"✓ Changes committed: {commit_msg.split(chr(10))[0]}")
            else:
                print(f"✗ Commit failed: {git_result['stderr']}")
        else:
            print(f"✗ Failed to stage files: {git_result['stderr']}")

    print("\n" + "=" * 60)
    print("Scenario Complete")
    print("=" * 60)

    return result['success']


if __name__ == "__main__":
    success = run_simple_cube_scenario()
    sys.exit(0 if success else 1)
