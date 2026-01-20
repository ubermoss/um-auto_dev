# Project Structure - UM-Auto_Dev

This document explains the three-layer architecture of the autonomous development system.

## The Three Layers

### 🧠 Layer 1: Meta-Framework (The Development Team)
**Location:** `meta_framework/`

This is the AI development system itself - the "team" that iterates on improvements.

```
meta_framework/
├── agents/                          # Specialized AI agents
│   ├── evaluator/                   # Visual analysis & scoring
│   │   └── visual_evaluator.py      # Analyzes renders, identifies issues
│   ├── planner/                     # Decision making
│   │   └── action_planner.py        # Converts issues → actionable changes
│   ├── executor/                    # Implementation (future)
│   ├── architect/                   # System enhancement (future)
│   └── human_interface/             # Human review packages (future)
│
├── tools/                           # Foundational tools
│   ├── state/                       # Conversation state tracking
│   ├── executor/                    # Blender execution
│   ├── git/                         # Version control
│   └── blender/                     # Blender script generation
│
└── iteration_loop/                  # Core orchestration
    └── coordinator.py               # Eval → Plan → Execute loop
```

**Key Components:**

- **VisualEvaluator** - Acts as "art director", analyzes renders against goals
- **ActionPlanner** - Converts evaluation feedback into executable actions
- **IterationCoordinator** - Orchestrates the complete iteration cycle

### ⚙️ Layer 2: Control Systems (The Tools Being Used)
**Location:** `control_systems/`

These are the systems the meta-framework manipulates to create outputs.

```
control_systems/
└── blender/                         # Blender control system
    ├── script_gen/                  # Script generation (future)
    ├── render_control/              # Render settings (future)
    └── scene_manipulation/          # Scene modification (future)
```

**Future additions:**
- `unity/` - Unity game engine control
- `unreal/` - Unreal Engine control
- `python/` - General Python project control
- Any other target system

### 🎯 Layer 3: Test Projects (The Artifacts)
**Location:** `test_projects/`

Actual projects used to validate the meta-framework works.

```
test_projects/
└── car_room_render/                 # Current test project
    ├── assets/                      # Scene files & resources
    │   ├── Ford_Capri_2024.blend   # Original car model
    │   ├── main.blend               # Working scene
    │   └── h3d_tire_sidewall.png   # Textures
    ├── expectations/                # What good looks like (future)
    └── iterations/                  # Generated iteration data
        └── {session_id}/
            ├── render_iter_001.png  # Renders from each iteration
            ├── iteration_001.json   # Evaluation & plan data
            └── session_results.json # Complete session summary
```

## The Iteration Loop

```
┌─────────────────────────────────────────────────────────────┐
│  Goal: "Make car render look professional"                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   1. RENDER          │ ◄──────┐
          │   Execute current    │        │
          │   scene state        │        │
          └──────────┬───────────┘        │
                     │                     │
                     ▼                     │
          ┌──────────────────────┐        │
          │   2. EVALUATE        │        │
          │   VisualEvaluator    │        │
          │   scores & analyzes  │        │
          └──────────┬───────────┘        │
                     │                     │
                     ▼                     │
          ┌──────────────────────┐        │
          │   3. PLAN            │        │
          │   ActionPlanner      │        │
          │   decides changes    │        │
          └──────────┬───────────┘        │
                     │                     │
                     ▼                     │
          ┌──────────────────────┐        │
          │   4. EXECUTE         │        │
          │   Apply changes      │        │
          │   to scene           │        │
          └──────────┬───────────┘        │
                     │                     │
                     ▼                     │
          ┌──────────────────────┐        │
          │   5. CHECK           │        │
          │   Goal achieved?     │        │
          │   Need human input?  │        │
          └──────────┬───────────┘        │
                     │                     │
        ┌────────────┴────────────┐       │
        │ NO                  YES │       │
        ▼                         ▼       │
    [Continue] ───────────►  [Stop]      │
        │                                 │
        └─────────────────────────────────┘
```

## Current Implementation Status

### ✅ Implemented (MVP)

- **Meta-Framework:**
  - VisualEvaluator with structured feedback format
  - ActionPlanner with capability detection
  - IterationCoordinator orchestrating the loop
  - Simulation mode for testing without actual rendering

- **Control Systems:**
  - Basic Blender capabilities defined
  - BlenderExecutor for script execution
  - BlenderTools for script generation

- **Test Projects:**
  - Car room render project structure
  - Ford Capri assets in place
  - Session tracking and data persistence

### 🚧 In Progress

- **Vision API Integration:**
  - VisualEvaluator uses simulated scoring
  - Need to integrate Claude's vision API for real analysis

- **Actual Execution:**
  - ActionPlanner creates plans
  - Need to translate plans → Blender scripts → execution

- **Human Interface:**
  - Basic recommendation generation works
  - Need richer visual presentation

### 🎯 Next Steps

1. **Integrate Vision API** - Replace simulated evaluation with real visual analysis
2. **Connect Execution** - Make ActionPlanner changes actually modify scenes
3. **Add System Architect** - Agent that enhances the framework when capabilities are missing
4. **Build Human Interface** - Rich HTML/markdown reports with visual comparisons
5. **Add Reference Images** - Support "make it look like this" workflows

## Running the System

### Quick Test (Simulated)
```bash
python test_iteration_loop.py
```

This runs 3 iterations with simulated evaluation to verify the loop works.

### With Actual Rendering (Future)
```bash
python run_project.py test_projects/car_room_render --max-iterations 10
```

## Key Design Decisions

### Why Three Layers?

1. **Separation of Concerns:** Meta-framework doesn't know about Blender specifics
2. **Reusability:** Same meta-framework can work with Unity, Unreal, Python, etc.
3. **Testability:** Can test framework with different target systems
4. **Clarity:** Clear what's "the system" vs. "what it builds"

### Why Short Iterations (2-3)?

- Every iteration should have **merit** - not throwing things at the wall
- Forces thoughtful, measured changes
- Easier to identify what caused improvements/regressions
- More human-manageable review sessions
- Token-efficient

### Why Human Review?

The system identifies when it needs human input:
- **Questions accumulated** - Style choices, preferences, requirements
- **Goal achieved** - Show success, get validation
- **Stagnation detected** - No progress, need different approach
- **System limitations** - Missing capabilities blocking progress

## File Organization

### Generated Data
All iteration data is timestamped and organized:
```
test_projects/{project}/iterations/{YYYYMMDD_HHMMSS}/
├── render_iter_001.png
├── render_iter_002.png
├── iteration_001.json       # Full iteration data
├── iteration_002.json
└── session_results.json     # Human review package
```

### Version Control
- Only code and configs are committed
- .blend files excluded (large binaries)
- Iteration data in .gitignore (can be large)
- Git notes for agent reasoning (agentic-commit skill)

## Architecture Alignment

This structure implements concepts from `AI-Driven Autonomous Development Shell.md`:

- **Cognitive Repository:** Git notes for reasoning persistence
- **Visual Grounding:** VisualEvaluator provides sensory feedback
- **Agentic CI/CD:** Iteration loop is continuous integration
- **Micro-Branching:** Each session gets own branch (future)
- **Shadow History:** Metadata alongside commits

## Extensibility

### Adding a New Control System

1. Create `control_systems/{new_system}/`
2. Define capabilities.json
3. Implement executor interface
4. Add to coordinator's system map

### Adding a New Agent

1. Create `meta_framework/agents/{new_agent}/`
2. Define agent interface
3. Integrate into coordinator
4. Update capabilities as needed

### Adding a New Test Project

1. Create `test_projects/{new_project}/`
2. Add assets to `assets/`
3. Define expectations (optional)
4. Run coordinator with new project path
