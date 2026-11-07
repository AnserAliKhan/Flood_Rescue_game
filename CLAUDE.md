# Flood Rescue: Project Rules

University Computational Thinking project. Python + Pygame only.
The student is beginner-to-intermediate: simple, well-commented code, no needless
abstraction or OOP for its own sake. The student must be able to explain every line.
Make use of recursion, loop , list , dictionaries where possible as these are concepts to be demonstrated. You many use other stuff too as per the requirement of the task

## Source of truth (read in this order)
1. docs/DECISIONS.md (overrides everything)
2. docs/SPEC.md
3. The feature file named in the prompt (docs/features/)

## Rules
- Pure logic modules (grid, entities, sandbags, pathfinding, scoring,
  level_generator) must NOT import pygame. Only interface/game/flood/main may.
- Grid is a 2D list: grid[row][col], 10 rows x 30 cols. Rendering must read from
  this data, never duplicate it.
- Connectivity is 4-direction only (up/down/left/right). Never diagonal.
- Backend decides results first; animation only displays them.
- Use constants/config for tunable values (bonus weight, sandbag margin, cell size).
- Write unit tests (pytest) for all pure logic.

## Workflow (spec-driven)
1. For each feature, I give you a spec in docs/features/. Do NOT build anything
   until a plan exists.
2. PLAN step: write the implementation plan to docs/plans/<feature-name>-plan.md
   (files to touch, function signatures, tests, risks). Then STOP and wait.
3. IMPLEMENT step (only when I say so): implement exactly the plan, nothing more.
4. At the end of a feature, report: what was built, important code sections,
   Python concepts used, how to run and test it, known limitations.
   Then STOP. Never start the next feature.
5. If the feature spec conflicts with DECISIONS.md or is ambiguous, ask me. Do not guess.