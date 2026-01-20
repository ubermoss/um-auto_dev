# Agentic Commit Skill (Project-Specific)

Advanced git commit workflow for the UM-Auto_Dev project that follows the Agentic Shell Architecture.

## Instructions

This skill extends the standard commit workflow with agent-specific metadata and visual artifact tracking as described in the project's architecture document.

When this skill is invoked:

1. **Standard Commit Flow**
   - Follow all steps from the global `commit-push` skill:
     - Check git status
     - Review and stage changes
     - Generate commit message
     - Get user approval

2. **Attach Agent Reasoning (Git Notes)**
   - After creating the commit, attach agent metadata using git notes
   - Create a JSON payload in the `refs/notes/agent-reasoning` namespace:
     ```json
     {
       "agent_id": "claude-sonnet-4.5",
       "timestamp": "<ISO8601>",
       "reasoning_trace": "<Brief explanation of approach and decisions>",
       "visual_artifact_refs": ["<paths to .blend files or renders>"],
       "execution_results": {
         "success": true/false,
         "test_scenario": "<scenario name if applicable>"
       }
     }
     ```
   - Attach the note with:
     ```bash
     git notes --ref=agent-reasoning add -m '<JSON>' <commit-sha>
     ```

3. **Link Visual Artifacts**
   - If the commit involves Blender files (.blend) or renders (.png, .jpg):
     - List the visual artifacts in the note metadata
     - These artifacts should be tracked in the commit itself
     - Record their relative paths from project root

4. **Branch Naming Convention**
   - For scenario executions: `scenario-<name>-<timestamp>`
   - For feature development: `agent/task-<id>-<description>`
   - For experimental branches: `agent/experiment-<description>-<variant>`

5. **Commit Message Format**
   - Follow the architecture's format:
     - First line: `<Type>: <Brief summary>` (50 chars max)
     - Types: `Scenario`, `Feature`, `Fix`, `Refactor`, `Experiment`
     - Blank line
     - Detailed description if needed
     - Blank line
     - Co-authorship line

6. **Handle Test Scenarios Specially**
   - If committing a test scenario execution:
     - Include scenario name in commit title
     - Add scenario results summary in commit body
     - Ensure generated scripts and output files are included
     - Update state JSON files

7. **Visual Verification Reference**
   - If applicable, note in the git note what visual verification was performed:
     - "Blender execution successful, objects created as expected"
     - "Render output matches expected visual fidelity"
     - "Scene file opens without errors"

## Example Commit with Note

```bash
# Create commit
git commit -m "$(cat <<'EOF'
Scenario: Simple Cube Scene

Generated and executed simple cube scene with red material.
- Created RedCube with 2x2x2 scale
- Applied red material
- Configured camera and lighting
- Rendered with Cycles (128 samples)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Attach reasoning note
COMMIT_SHA=$(git rev-parse HEAD)
git notes --ref=agent-reasoning add -m '{
  "agent_id": "claude-sonnet-4.5",
  "timestamp": "2026-01-20T21:02:12Z",
  "reasoning_trace": "Created declarative scenario JSON and executed through BlenderExecutor. All steps completed successfully with visual verification.",
  "visual_artifact_refs": [
    "test_scenarios/simple_cube/output/red_cube_scene.blend",
    "test_scenarios/simple_cube/output/generated_scene.py"
  ],
  "execution_results": {
    "success": true,
    "test_scenario": "simple_cube",
    "blender_version": "5.0",
    "return_code": 0
  }
}' $COMMIT_SHA
```

## Viewing Agent Reasoning

To view the agent reasoning for any commit:
```bash
git log --show-notes=agent-reasoning
```

To view reasoning for specific commit:
```bash
git notes --ref=agent-reasoning show <commit-sha>
```

## Safety Rules

- Always validate JSON before attaching notes
- Don't attach notes to commits from before this architecture was implemented
- Keep reasoning traces concise but informative
- Always include success/failure status in execution results

## Notes

- This skill is project-specific to um-auto_dev
- It implements the "Cognitive Repository" concept from the architecture
- Git notes don't change commit SHAs, so they're safe to add post-commit
- Notes are pushed with: `git push origin refs/notes/agent-reasoning`
