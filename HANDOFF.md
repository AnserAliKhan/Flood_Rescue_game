# Project Handoff: Flood Rescue

## 1. Project Overview
**Flood Rescue** is a 2D grid-based puzzle game developed for a University Computational Thinking course. The objective is to evacuate people from various buildings (Houses, Schools, Hospitals) to a designated Shelter by constructing efficient paths using a limited number of sandbags.
- **Intended Users**: Academic evaluation (student and instructor).
- **Final Outcome**: A functional game where players strategically place sandbags to connect buildings to a shelter, with scoring based on people saved and sandbags conserved.

## 2. Technology Stack
- **Language**: Python 3.12+
- **GUI Framework**: Pygame
- **Testing**: pytest
- **Architecture**: Modular separation of "Pure Logic" (grid, entities, sandbags, pathfinding, scoring, game state) and "Interface" (rendering and input handling).
- **Data Structure**: The game world is represented as a 2D list (`grid[row][col]`).

## 3. Feature Implementation Status
| Feature | Status | Description | Dependencies | Outstanding Work |
| :--- | :--- | :--- | :--- | :--- |
| **F00: Skeleton** | Completed | Pygame window, main loop, basic config. | None | None |
| **F01: Grid** | Completed | 30x10 2D list, rendering, pixel-to-cell mapping. | F00 | None |
| **F02: Entities** | Completed | House, School, Hospital, Shelter data models. | F01 | None |
| **F03: Sandbags** | Completed | Placement, removal, budget counting, validation. | F02 | None |
| **F04: Connectivity** | Completed | Recursive DFS from shelter to buildings. | F03 | None |
| **F05: Scoring** | Completed | Pop score, conditional efficiency bonus, breakdown. | F04 | None |
| **F06: State Machine** | Completed | Planning $\rightarrow$ Confirm $\rightarrow$ Results flow. | F05 | None |
| **F07: Flood Animation** | Pending | Visual flood effect and results display. | F06 | Full implementation |
| **F08: Level Gen** | Pending | Random building placement and population logic. | F06 | Full implementation |
| **F09: Baseline Calc** | Pending | Algorithm to calculate minimum sandbags. | F08 | Full implementation |
| **F10: Levels/Prog** | Pending | Level switching and final game summary. | F09 | Full implementation |
| **F11: Polishing** | Pending | UI improvements, instructions, final bug fixes. | F10 | Full implementation |

## 4. Development History
- **Architecture**: Established a strict rule where logic modules (grid, entities, etc.) must not import Pygame.
- **Key Decisions**:
    - **Decision D1**: Fixed population totals per level.
    - **Decision D3**: 4-direction connectivity; buildings can relay the network.
    - **Decision D5 (Amended)**: Efficiency bonus is granted ONLY if all people are saved.
    - **Decision D7**: Progression to the next level requires saving everyone.
- **Implemented**: Basic loop, grid rendering, entity placement, sandbag budget management, recursive connectivity check, and the state machine for game flow.

## 5. Current Codebase
### Core Directories
- `/docs`: Contains the source of truth (`SPEC.md`, `DECISIONS.md`) and feature specs (`/features`).
- `/docs/plans`: Implementation plans for completed features.
- `/tests`: Pytest suites for every logic module.

### Important Files
- `config.py`: All tunable constants, colors, and the `ALLOWED_TRANSITIONS` table for the state machine.
- `grid.py`: 2D list management and coordinate conversion logic.
- `entities.py`: Entity record dictionaries and placement logic.
- `sandbags.py`: Sandbag counting and validation.
- `pathfinding.py`: Recursive DFS and iterative cross-checks for connectivity.
- `scoring.py`: Scoring calculations and the results breakdown dictionary.
- `game.py`: State machine logic (transitions, confirmation, retry).
- `interface.py`: All Pygame rendering calls.
- `main.py`: Entry point; routes input based on current state.

## 6. Git Status
- **Branch**: `main`
- **Status**: Working tree clean.
- **Latest Commits**: Feature F00 through F06 are committed and verified.

## 7. Known Issues
- **Current State**: The game uses a temporary `TEST_SANDBAG_BUDGET` and a hard-coded `TEST_LAYOUT` for testing.
- **Placeholder**: The "Continue" button in the results phase shows a placeholder message.

## 8. Testing
- **How to run**: 
    - App: `python main.py`
    - Tests: `pytest`
- **Verified**: All logic modules (grid, entities, sandbags, pathfinding, scoring, game) have 100% pass rates on their respective pytest suites.

## 9. Development Instructions
- **Constraints**:
    - **NO Pygame in logic**: `grid.py`, `entities.py`, `sandbags.py`, `pathfinding.py`, `scoring.py`, and `game.py` must remain pure Python.
    - **Grid Source of Truth**: Rendering and scoring must read from the grid data, not duplicate it.
    - **Beginner Friendly**: Code must be simple and well-commented. Avoid unnecessary OOP or complex abstractions.
- **Workflow**:
    1. Read the feature spec in `docs/features/`.
    2. Create a plan in `docs/plans/`.
    3. Implement the plan.
    4. Write pytest tests for logic.
    5. Report and STOP.

## 10. Next Steps
The next developer should begin with **Feature F07: Flood Animation**. This involves:
1. Creating a `flood.py` module to handle the timing and progression of the flood.
2. Updating `interface.py` to visually render the flood filling the grid.
3. Updating `main.py` and `game.py` to insert the "flooding" phase between `PHASE_CONFIRMING` and `PHASE_RESULTS`.

## 11. Instructions for the Next Agent
- Start by reading `CLAUDE.md` and `docs/DECISIONS.md` to understand the project's strict academic constraints.
- Follow the established workflow: **Spec $\rightarrow$ Plan $\rightarrow$ Implement $\rightarrow$ Test $\rightarrow$ Report**.
- Do not rewrite existing logic unless requested; the current logic modules are fully tested and verified.
- Maintain the separation between `interface.py` (drawing) and `game.py`/`pathfinding.py` (logic).
