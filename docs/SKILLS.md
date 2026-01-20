# Skills Reference

This project uses both global and project-specific Claude Code skills for git workflows.

## Global Skills

Located in `~/.claude/skills/` - available in all projects.

### `/git-init` - Initialize Git Repository
**Purpose:** Initialize a new git repository with proper setup

**Usage:**
```
/git-init
```

**What it does:**
- Checks if git is already initialized
- Runs `git init`
- Offers to create `.gitignore` based on project type
- Suggests creating README if missing
- Shows initial `git status`

**When to use:** Starting a new project or adding git to an existing folder

---

### `/commit-push` - Commit and Push Changes
**Purpose:** Complete workflow for committing and pushing changes

**Usage:**
```
/commit-push
/commit-push -m "Custom commit message"
```

**What it does:**
1. Checks git status and shows changes
2. Warns about sensitive files (.env, credentials, etc.)
3. Stages changes (`git add .`)
4. Generates intelligent commit message based on changes
5. Creates commit with co-authorship attribution
6. Checks/configures remote repository
7. Pushes changes to remote
8. Confirms completion

**Safety features:**
- Warns about sensitive files
- Never force pushes without confirmation
- Follows repository commit message style
- Includes co-authorship line

---

## Project-Specific Skill

Located in `.claude/skills/` - only available in this project.

### `/agentic-commit` - Agentic Architecture Commit
**Purpose:** Advanced commit with agent reasoning metadata (implements Cognitive Repository pattern)

**Usage:**
```
/agentic-commit
```

**What it does:**
All features of `/commit-push` plus:
1. Attaches git notes with agent reasoning metadata
2. Links visual artifacts (.blend files, renders)
3. Records execution results
4. Follows agentic branch naming conventions
5. Special handling for test scenario commits

**Git Notes Structure:**
```json
{
  "agent_id": "claude-sonnet-4.5",
  "timestamp": "ISO8601",
  "reasoning_trace": "Decision explanation",
  "visual_artifact_refs": ["paths to visual files"],
  "execution_results": {
    "success": true/false,
    "test_scenario": "scenario name"
  }
}
```

**View agent reasoning:**
```bash
git log --show-notes=agent-reasoning
git notes --ref=agent-reasoning show <commit-sha>
```

**Push notes to remote:**
```bash
git push origin refs/notes/agent-reasoning
```

---

## When to Use Which Skill

| Scenario | Skill | Reason |
|----------|-------|--------|
| Brand new folder, no git | `/git-init` | Initialize repository |
| Regular code changes | `/commit-push` | Standard commit workflow |
| Test scenario execution | `/agentic-commit` | Track agent metadata |
| Blender scene modifications | `/agentic-commit` | Link visual artifacts |
| Experimental branches | `/agentic-commit` | Record reasoning |
| Quick fixes in other projects | `/commit-push` | Global, no extra metadata |

---

## Architecture Alignment

The `/agentic-commit` skill implements concepts from `AI-Driven Autonomous Development Shell.md`:

- **Section 2.2.1:** Git notes for "invisible metadata"
- **Cognitive Repository:** Agent reasoning persistence
- **Visual Artifact Linking:** Binding ephemeral visuals to persistent code history
- **Shadow History:** Parallel metadata stream alongside commit history

---

## Creating Your Own Skills

Global skills: `~/.claude/skills/<name>.md`
Project skills: `./.claude/skills/<name>.md`

Skills are markdown files with:
- Clear instructions for Claude
- Example usage
- Safety rules
- Expected behavior

See existing skills for reference templates.
