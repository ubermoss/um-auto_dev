# UM-Auto_Dev - Autonomous Blender Development Shell

An AI-driven development environment for automated Blender scene creation, manipulation, and version control.

## Overview

This project provides tools for autonomously generating and executing Blender Python scripts through a conversation-driven workflow. It includes state management, git integration, and automated testing capabilities.

## Components

### Core Tools (`tools/`)

- **state/state_manager.py** - Tracks conversation state and execution history
- **executor/executor.py** - Executes Python scripts in Blender
- **git/git_tools.py** - Version control operations
- **blender/blender_tools.py** - Blender script generation utilities

### Test Scenarios (`test_scenarios/`)

Each test scenario includes:
- `scenario.json` - Declarative scenario definition
- `run_scenario.py` - Scenario execution script
- `output/` - Generated scripts and blend files

## Quick Start

### Prerequisites

- Python 3.10+
- Blender 5.0 (default path: `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`)
- Git

### Running a Test Scenario

```bash
python test_scenarios/simple_cube/run_scenario.py
```

This will:
1. Create a git branch for the scenario
2. Generate Blender Python scripts based on scenario steps
3. Execute the scripts in Blender (background mode)
4. Save the resulting .blend file
5. Commit changes to git

## Project Structure

```
um-auto_dev/
├── tools/                      # Core Python tools
│   ├── state/                  # State management
│   ├── executor/               # Blender execution
│   ├── git/                    # Git operations
│   └── blender/                # Blender utilities
├── test_scenarios/             # Test scenarios
│   └── simple_cube/            # Example: red cube scene
│       ├── scenario.json       # Scenario definition
│       ├── run_scenario.py     # Scenario runner
│       └── output/             # Generated files
├── assets/                     # Blender assets
│   └── Ford_Capri_2024_blend/ # Car model
│       └── main.blend          # Car scene file
└── logs/                       # Execution logs
```

## Assets

### Ford Capri 2024
Located in `assets/Ford_Capri_2024_blend/main.blend`

This is a complete car model that can be used for testing scene manipulation, camera positioning, and rendering workflows.

## Scenario Format

Scenarios are defined in JSON with the following structure:

```json
{
  "name": "Scenario Name",
  "description": "What this scenario does",
  "steps": [
    {
      "id": 1,
      "type": "create_object",
      "description": "Human readable step description",
      "object_type": "cube",
      "parameters": { }
    }
  ],
  "expected_output": { }
}
```

### Supported Step Types

- `create_object` - Create primitives (cube, sphere, etc.)
- `apply_material` - Apply materials and colors
- `setup_camera` - Position and configure cameras
- `setup_light` - Add lighting to scene
- `configure_render` - Set render engine and settings
- `save_file` - Save .blend file

## Features

- Declarative scenario definitions
- Automated script generation
- Git branching per scenario
- Execution state tracking
- Background Blender execution
- Automatic result verification

## Development Status

Currently implemented (MVP):
- Core tool framework
- Simple cube test scenario
- Git integration
- State management
- Script generation and execution

## Future Enhancements

See `AI-Driven Autonomous Development Shell.md` for the full roadmap including:
- Natural language conversation interface
- Multi-turn conversation support
- Error recovery and iterative refinement
- Advanced scene manipulation
- Render job automation
- Claude MCP integration

## Example Output

The simple cube scenario generates:
- `generated_scene.py` - Combined Blender Python script
- `red_cube_scene.blend` - Final scene file with red cube, camera, and lighting
- `scenario_state.json` - Execution state and history
- Git commit with all changes
