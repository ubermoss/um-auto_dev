# Integration Guide: Claude Code + Meta-Framework

This guide explains how **I (Claude Code)** use the meta-framework to autonomously improve visual projects.

## Core Principle

**I am the LLM for ALL LLM operations.**

- **Python framework** = Dumb infrastructure (file I/O, Blender execution, data management)
- **Claude Code (me)** = Intelligence (vision, decisions, reasoning, code generation)

## Architecture

### What I Do (Intelligence)
- Visual evaluation using my vision capability
- Strategic decisions and planning
- Code generation when new tools needed
- Research via WebSearch
- Human interaction and presentation
- Sub-agent orchestration via Task tool

### What Python Does (Infrastructure)
- Execute Blender scripts
- Manage session state persistence
- Track capabilities
- Handle file I/O
- Run calculations

## Session Workflow

### 1. You Ask Me to Improve Something

```
YOU: "Improve the car render for a vehicle configurator"
```

### 2. I Bootstrap the Session

```python
ME: Let me check what sessions exist for this project...

<bash: python meta_framework/cli/session_tools.py list test_projects/car_room_render>
→ Returns: {"sessions": []}  # New project

ME: Starting new session...

<bash: python -c "
from meta_framework.data.session_state import SessionState
from datetime import datetime
session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
state = SessionState(session_id, 'test_projects/car_room_render')
state.save()
print(session_id)
">
→ Returns: "20260120_220315"

ME: Session 20260120_220315 created
```

### 3. I Spawn Project Analyst Sub-Agent

```python
ME: Let me understand what we're building...

<use Task tool>
subagent_type: "general-purpose"
model: "sonnet"
prompt: """**Your Role:** Project domain expert

[Includes agent_definitions.py prompt for project_analyst]

**Scene Information:**
Ford Capri car model in studio room
Basic lighting setup
Professional quality asset

**User's Goal:**
Vehicle configurator renders

**Analyze the project type and requirements...**
"""
```

**Project Analyst Returns:**
```json
{
  "project_type": "automotive_product_visualization",
  "domain": "automotive_marketing",
  "confidence": 0.95,
  "likely_requirements": {
    "multiple_angles": 0.90,
    "color_variants": 0.75,
    "turntable_360": 0.65,
    "interactive": 0.60
  },
  "recommended_roadmap": "Option B: Multi-angle system",
  "reasoning": "Asset quality suggests professional use case..."
}
```

### 4. I Set Session Context

```python
ME: <bash: python -c "
from meta_framework.data.session_state import SessionState
state = SessionState('20260120_220315', 'test_projects/car_room_render')
state.set_project_info(
    project_type='automotive_product_visualization',
    goal='Vehicle configurator renders - multi-angle system',
    domain='automotive_marketing'
)
">

ME: Project understanding set. This is automotive visualization.

ME (presenting to you):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: Automotive Product Visualization
Confidence: 95%

Likely Needs:
✓ Multiple camera angles (90% probability)
✓ Color variants (75%)
✓ 360° turntable (65%)

Recommended Approach:
Option B: Multi-angle System
- 5-7 standard angles
- Consistent lighting rig
- Batch rendering
- 8-12 iterations estimated

Shall I proceed with this roadmap? [Y/n/customize]
```

### 5. I Render and Evaluate

```python
YOU: Yes, proceed

ME: Starting iteration loop...

<bash: python -c "
from meta_framework.tools.executor.executor import BlenderExecutor
from pathlib import Path

executor = BlenderExecutor()
scene = 'test_projects/car_room_render/assets/main.blend'
output = 'test_projects/car_room_render/iterations/20260120_220315/render_001.png'

Path(output).parent.mkdir(parents=True, exist_ok=True)

result = executor.execute_inline(f'''
import bpy
bpy.context.scene.render.filepath = \"{output}\"
bpy.ops.render.render(write_still=True)
print(\"Render complete\")
''', blend_file=scene)

print(result['success'])
">

ME: Render complete. Let me evaluate it...

<read render_001.png as image using my vision>

ME (analyzing with MY vision):
I see a Ford Capri in a simple room. Major issues:

1. SEVERELY UNDEREXPOSED
   - Car is barely visible
   - 80%+ of image is near black
   - This is the most critical issue

2. FLAT LIGHTING
   - No depth perception
   - Single light source insufficient
   - Missing rim/accent lighting

3. DULL MATERIALS
   - Car paint lacks luster
   - No environment reflections
   - Needs proper HDRI

Current score: 35/100 (not usable)
```

### 6. I Assess System Needs

```python
ME: Let me check what capabilities we have...

<bash: python meta_framework/cli/session_tools.py check histogram_analyzer hdri_loader material_optimizer>
→ Returns: {
  "missing": ["histogram_analyzer", "hdri_loader", "material_optimizer"],
  "all_present": false
}

ME: We're missing critical tools. Spawning Technical Architect...

<use Task tool>
subagent_type: "general-purpose"
model: "sonnet"
prompt: [architect prompt with evaluation and capabilities]
```

**Technical Architect Returns:**
```json
{
  "capability_gaps": [
    {
      "name": "histogram_analyzer",
      "priority": "critical",
      "reasoning": "Can't measure exposure objectively",
      "blocks": "Data-driven lighting decisions"
    },
    {
      "name": "hdri_loader",
      "priority": "high",
      "reasoning": "Essential for realistic car materials",
      "blocks": "Professional material quality"
    }
  ],
  "build_order": ["histogram_analyzer", "hdri_loader"],
  "estimated_effort": "2-3 hours development"
}
```

### 7. I Build Missing Tools

```python
ME: Building histogram_analyzer first...

<use Task tool>
subagent_type: "general-purpose"
model: "sonnet"
prompt: [tool_builder prompt with histogram_analyzer spec]
```

**Tool Builder Returns:**
```python
# Complete histogram_analyzer.py code
```

```python
ME: <write meta_framework/tools/vision/histogram_analyzer.py with the code>

ME: Testing the tool...

<bash: python -c "
from meta_framework.tools.vision.histogram_analyzer import analyze_histogram
result = analyze_histogram('test_projects/car_room_render/iterations/20260120_220315/render_001.png')
print(result)
">

→ Returns: {
  "mean_luminance": 0.12,
  "target_luminance": 0.50,
  "suggested_multiplier": 4.2,
  "dark_pixels_percent": 78
}

ME: Tool works! Committing...

<git add meta_framework/tools/vision/histogram_analyzer.py>
<git commit -m "Add histogram analyzer for data-driven lighting">

ME: Recording capability...

<bash: python -c "
from meta_framework.data.capability_registry import CapabilityRegistry
from meta_framework.data.session_state import SessionState

registry = CapabilityRegistry()
registry.add_capability(
    name='histogram_analyzer',
    category='vision',
    description='Analyzes render exposure via histogram',
    operations=['analyze_exposure', 'suggest_lighting_adjustment']
)

state = SessionState('20260120_220315', 'test_projects/car_room_render')
state.add_capability('histogram_analyzer', 'Enables data-driven lighting decisions')
">
```

### 8. I Apply Changes

```python
ME: Now using histogram data to fix lighting...

Histogram shows: Need 4.2x more light
Current key light: 1.5
Target: 6.3

<write Blender script to adjust lighting>
<execute script>
<render again>

ME: Checking improvement...

<read new render with my vision>

ME: Much better!
Score improved: 35 → 68 (+33 points)

Saving iteration...

<bash: python -c "
from meta_framework.data.session_state import SessionState

state = SessionState('20260120_220315', 'test_projects/car_room_render')
state.add_iteration({
    'iteration': 1,
    'summary': 'Fixed exposure using histogram analysis',
    'score_before': 0.35,
    'score_after': 0.68,
    'key_changes': [
        'Increased key light 1.5 → 6.3 (histogram-driven)',
        'Added fill light at 3.0'
    ],
    'system_enhancements': ['histogram_analyzer'],
    'insights': ['Histogram-driven lighting is essential'],
    'render_path': 'render_002.png',
    'next_action': 'Improve materials with HDRI'
})
">
```

### 9. I Present to You

```python
ME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ITERATION 1 COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Visual Improvement:
Score: 35 → 68 (+33 points)

Before: [shows image]
After:  [shows image]

Changes Made:
✓ Increased key light intensity (data-driven)
✓ Added fill light to prevent harsh shadows
✓ Adjusted based on histogram analysis

System Evolution:
✓ Created histogram_analyzer.py
✓ Committed to meta_framework
✓ Now have objective exposure measurement

Insights Learned:
- Histogram analysis essential for lighting
- Need 4-5x more light than initial guess
- Data-driven > intuition-based adjustments

Still Need:
- HDRI environment for car materials
- Rim lighting for depth
- Composition refinement

Continue to iteration 2? [Y/n]
```

## Resuming Sessions

### When Context Runs Out

```python
YOU: "Continue improving the car render"

ME: Let me find the session...

<bash: python meta_framework/cli/session_tools.py list test_projects/car_room_render>
→ Returns: [{"session_id": "20260120_220315", "summary": "3 iterations, score 84%", ...}]

ME: Loading session 20260120_220315...

<bash: python meta_framework/cli/session_tools.py info test_projects/car_room_render 20260120_220315>
→ Returns: complete session state

ME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESUMING SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: Automotive Visualization
Goal: Vehicle configurator - Multi-angle system

Progress: 3 iterations completed
Score: 35% → 84% (+49 points)

System Evolution:
✓ histogram_analyzer
✓ hdri_loader
✓ automotive_materials

Recent Work (Iteration 3):
- Refined composition
- Simplified background
- Adjusted camera angle

Current Status: [shows last render]

Next Steps:
- Move to multi-angle system
- Create camera rig

Continue where we left off? [Y/n]
```

## Key Files

### Session State
`test_projects/{project}/iterations/{session_id}/session_state.json`

Contains everything needed to resume:
- Project understanding
- Iteration history
- Capabilities added
- Pending decisions
- Next actions

### Capability Registry
`meta_framework/data/capabilities.json`

Tracks all system capabilities:
- What tools exist
- What they can do
- Success rates
- Usage stats

### Agent Definitions
`meta_framework/agents/agent_definitions.py`

Defines sub-agent roles for me to spawn:
- Project Analyst
- Art Director
- Technical Architect
- Tool Builder
- Research Specialist

## Benefits

### Token Efficiency
- Each sub-agent has narrow context
- Session state enables resuming
- No need to replay full history

### Focused Expertise
- Art Director only thinks about visuals
- Architect only thinks about system design
- Tool Builder only writes code

### Learning Across Projects
- Capabilities persist
- Knowledge accumulates
- Next project starts smarter

### Human Collaboration
- Clear decision points
- Transparent reasoning
- Visual progress tracking
