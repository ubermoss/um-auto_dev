# Current State - January 20, 2026

## What We've Built

### 🎯 The Three-Layer Architecture

Successfully separated the system into:

1. **Meta-Framework** (`meta_framework/`) - The AI development team
   - VisualEvaluator - Analyzes renders and provides structured feedback
   - ActionPlanner - Converts feedback into executable actions
   - IterationCoordinator - Orchestrates the eval→plan→execute loop

2. **Control Systems** (`control_systems/`) - The tools being manipulated
   - Blender control system structure
   - Capability definitions
   - Extensible to Unity, Unreal, Python, etc.

3. **Test Projects** (`test_projects/`) - The artifacts being created
   - Car room render project with Ford Capri assets
   - Iteration tracking and session data
   - Ready for actual render testing

### ✅ Working MVP

The iteration loop successfully:
- Runs 2-3 iteration cycles
- Simulates evaluation (structure ready for vision API)
- Plans actions based on feedback
- Tracks what decisions were made
- Identifies when system enhancements are needed
- Generates human review packages
- Saves all session data

**NEW:** Token tracking system with three layers:
- Meta-meta: Framework development overhead tracking
- Meta: Iteration execution with learning
- Project: Target operations (cheap)
- Proactive warnings before expensive operations

**Test Output:**
```
Iteration 1: Score 0.60 → Identified "Scene too dark"
Iteration 2: Score 0.70 → Added "rim lighting"
Iteration 3: Score 0.80 → Reached max iterations
Final: +20% improvement, goal not yet achieved
```

### 📁 Project Structure

```
um-auto_dev/
├── meta_framework/              # Layer 1 - The AI System
│   ├── agents/
│   │   ├── evaluator/
│   │   └── planner/
│   ├── tools/
│   └── iteration_loop/
│
├── control_systems/             # Layer 2 - Target Systems
│   └── blender/
│
├── test_projects/               # Layer 3 - Test Artifacts
│   └── car_room_render/
│       ├── assets/              # Ford Capri .blend files
│       └── iterations/          # Generated session data
│
├── test_scenarios/              # Old structure (legacy)
├── docs/                        # Documentation
├── .claude/                     # Claude Code config & skills
│   └── skills/
│       └── agentic-commit.md    # Project-specific git skill
│
├── test_iteration_loop.py       # Quick test runner
├── PROJECT_STRUCTURE.md         # Architecture documentation
├── CURRENT_STATE.md            # This file
└── README.md                    # Project overview
```

## What's Working

### ✅ Core Loop
- Iteration coordinator successfully orchestrates 3 cycles
- State tracking between iterations
- Session data persistence
- Human review package generation

### ✅ Evaluation Framework
- Structured feedback format defined
- Technical and artistic quality metrics
- Critical issues vs. improvements prioritization
- Questions for human escalation
- Stopping criteria (max iterations, goal achieved, stagnation)

### ✅ Planning System
- Action creation from evaluation feedback
- Capability detection (can we execute this?)
- System enhancement tracking (what's missing?)
- Parameter extraction from natural language
- Impact estimation

### ✅ Documentation
- Complete architecture explanation
- Clear layer separation
- Extensibility guidelines
- Git skills (global + project-specific)

## What's Still Simulated

### 🎭 Needs Real Implementation

1. **Visual Evaluation** (Priority: HIGH)
   - Currently: Simulated scores that improve each iteration
   - Need: Claude vision API integration for real image analysis
   - Impact: This is the foundation of making good decisions

2. **Rendering** (Priority: HIGH)
   - Currently: Fake render paths generated
   - Need: Actually execute Blender renders via BlenderExecutor
   - Impact: Need real images to evaluate

3. **Action Execution** (Priority: HIGH)
   - Currently: Actions planned but not applied to scene
   - Need: Translate ActionPlanner output → Blender script changes
   - Impact: Loop won't improve scenes without this

4. **System Architect Agent** (Priority: MEDIUM)
   - Currently: Enhancement requests tracked but not implemented
   - Need: Agent that writes new BlenderTools methods when needed
   - Impact: System can't self-improve yet

5. **Human Interface Agent** (Priority: LOW)
   - Currently: JSON output with basic text formatting
   - Need: Rich HTML reports with visual comparisons
   - Impact: User experience, but not blocking core loop

## Critical Path to Real Iteration

### Phase 1: Get One Real Iteration Working
```
1. Integrate Vision API into VisualEvaluator
   → evaluate_render() calls Claude vision API
   → Returns real structured feedback

2. Connect Rendering
   → coordinator._render_scene() uses BlenderExecutor
   → Actually runs Blender and captures output

3. Implement One Action Type
   → Start with lighting adjustments (simplest)
   → ActionPlanner → Generate Blender script → Execute
   → Verify change was applied

TEST: Run 1 iteration, see actual improvement
```

### Phase 2: Complete the Loop
```
4. Implement remaining action types
   → Materials, camera, render settings
   → Test each type individually

5. Add error recovery
   → What if Blender crashes?
   → What if vision API fails?
   → Graceful degradation

TEST: Run 3 iterations, achieve goal
```

### Phase 3: System Self-Improvement
```
6. Build System Architect agent
   → Reads enhancement requests
   → Generates new BlenderTools methods
   → Tests and commits additions

7. Multi-project testing
   → Create 2-3 different test projects
   → Verify framework generalizes

TEST: System enhances itself when encountering new problems
```

## Decision Points

### 1. Vision API Integration
**Question:** Use Claude vision API or alternative?

**Options:**
- Claude vision API (native, high quality, integrated)
- GPT-4 vision (alternative, might be faster)
- Local vision model (fully autonomous, lower quality)

**Recommendation:** Start with Claude vision API
- Already using Claude ecosystem
- Highest quality analysis
- Can switch later if needed

### 2. Iteration Stop Criteria
**Current:** Fixed 3 iterations for testing

**Question:** Production stopping logic?

**Options:**
- Fixed count (simple, predictable)
- Score threshold (goal-oriented)
- Improvement rate (efficiency-focused)
- Question accumulation (human-need-based)
- Hybrid (all of the above)

**Recommendation:** Hybrid approach
- Max 10 iterations (safety)
- Stop if score > 0.85 (success)
- Stop if < 5% improvement in 3 iterations (stagnant)
- Stop if 3+ questions accumulated (need human)

### 3. System Enhancement Strategy
**Question:** How should the system improve itself?

**Options:**
- Manual: Human writes new capabilities when requested
- Semi-auto: System generates code, human reviews/commits
- Full-auto: System writes, tests, and commits enhancements

**Recommendation:** Start semi-auto
- System generates new BlenderTools methods
- Human reviews before committing
- Safety + autonomy balance

### 4. Multiple Target Systems
**Question:** When to add Unity/Unreal support?

**Recommendation:** After Phase 2
- Prove concept with Blender first
- Then generalize to other systems
- Having one working system makes patterns clear

## Token Usage Strategy

### Three-Layer Token Tracking System ✅

**Problem:** Hit token limit while building the meta-system itself (meta-meta layer)

**Solution:** Track token costs across all three layers:

1. **Meta-Meta Layer** (Framework Development)
   - **What:** Building the system that tracks tokens (this conversation)
   - **Tools:** `OperationCostEstimator` with rough estimates
   - **Triggers:** Refactoring, creating new tools, architecture changes
   - **Example:** "Refactor all token tracking code" = ~81,000 tokens
   - **Warning levels:** 80% checkpoint, 90% critical

2. **Meta Layer** (System Execution)
   - **What:** Running iteration loops, spawning sub-agents
   - **Tools:** `TokenTracker` with learned history (min 3 samples)
   - **Cost:** Medium (5,000-15,000 per iteration)
   - **Learning:** Records actual usage, improves estimates over time

3. **Project Layer** (Target Operations)
   - **What:** Blender renders, file I/O
   - **Cost:** Low (~500 tokens per render)
   - **No tracking needed:** Too cheap to matter

### Token Guard Integration
- `TokenGuard`: Simple warnings for meta layer operations
- `OperationCostEstimator`: Composite estimates for meta-meta layer
- **Proactive checking:** Via `token-check` skill (global .claude/skills/)
- **Non-blocking:** Shows warning, user decides

### Why 2-3 Iterations?
- Each iteration should be **thoughtful, not brute force**
- With vision API, each eval costs tokens
- Token tracking now accounts for all layers
- Human review every 3 iterations is manageable
- Can scale up once proven effective

### Optimization Opportunities
1. Cache evaluation prompts (don't rebuild each time)
2. Only send changed scene elements to vision (not full image)
3. Use Haiku for simple decisions, Sonnet for complex
4. Batch multiple evaluations in one API call (if possible)
5. **Meta-meta awareness:** Warn before expensive framework operations

## Next Session Tasks

### Immediate (Next 1-2 hours)
1. ✅ Commit current restructure to git
2. Integrate Claude vision API into VisualEvaluator
3. Connect BlenderExecutor rendering
4. Test one real iteration end-to-end

### Short Term (This week)
1. Implement all action execution types
2. Error handling and recovery
3. Create 2-3 more test projects
4. Document vision API integration

### Medium Term (This month)
1. Build System Architect agent
2. Self-improvement demonstration
3. Multi-project validation
4. Performance optimization

## Questions to Resolve

### Technical
- How to handle long Blender render times? (async?)
- Should we render at low quality for iteration speed? (yes, probably)
- How to version control scene changes? (git-appraise + notes)
- When to create new branches vs. continue on one? (every session)

### Product
- What makes a "good" automotive render? (need reference images)
- How much human guidance is too much? (vs. too little)
- Should system learn preferences over time? (future feature)
- How to handle subjective feedback? ("I don't like it")

### Architecture
- Should evaluator and planner be separate processes? (currently in-process)
- How to handle distributed execution? (future: cloud renders)
- Database vs. files for iteration tracking? (files for now)
- How to replay/debug past sessions? (already have JSON logs)

## Success Metrics

### For Next Session
- [ ] One real iteration completes successfully
- [ ] Vision API provides useful feedback
- [ ] One action type actually changes the scene
- [ ] Visual improvement is measurable

### For This Week
- [ ] 3 iteration loop achieves goal improvement
- [ ] All action types implemented
- [ ] Error recovery works
- [ ] Documentation is current

### For This Month
- [ ] System enhances itself once
- [ ] Works with 3+ different projects
- [ ] Human review is clear and actionable
- [ ] Token usage is optimized

## Notes & Observations

### What's Working Well
- Three-layer separation makes everything clearer
- Simulated evaluation helped validate the structure
- JSON-based communication is debuggable
- Session tracking gives full audit trail

### What Needs Improvement
- Too many hardcoded paths (make configurable)
- Error messages could be more helpful
- Need better progress visualization
- Documentation needs examples

### Interesting Discoveries
- Parameter extraction from natural language works surprisingly well
- The planner naturally prioritizes critical fixes
- 3 iterations feels about right for meaningful progress
- System enhancement tracking surfaces real gaps

## Repository Status

- **Branch:** `scenario-simple-cube-20260120_210212`
- **Commits:** 2 (initial setup + blend exclusion)
- **Remote:** https://github.com/ubermoss/um-auto_dev
- **Next Commit:** Should be the restructure + MVP iteration loop
