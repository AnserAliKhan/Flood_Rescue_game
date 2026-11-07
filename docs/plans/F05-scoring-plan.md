# Plan: F05 Scoring (Population Score, Conditional Efficiency Bonus, Breakdown)

## Context
This feature implements the scoring logic for the game. It calculates how many people were saved, the resulting population score, and a conditional efficiency bonus that is only awarded if all people in the level are saved. The final output is a detailed breakdown dictionary used for the results screen.

## Proposed Implementation

### 1. Files to Create or Change

- **`scoring.py` (CREATE)**: Pure logic module for score calculations. No Pygame imports.
- **`tests/test_scoring.py` (CREATE)**: Pytest suite to validate all scoring rules, invariants, and the conditional bonus.

### 2. Functions and Signatures

#### `scoring.py`
- `check_evaluated(entities) -> None`: Iterates through `entities`; raises `ValueError("Connectivity has not been evaluated")` if any non-shelter entity has `connected is None`.
- `count_saved_people(entities) -> int`: Sum of `population` for entities where `connected == True`.
- `count_unsaved_people(entities) -> int`: Sum of `population` for entities where `connected == False`.
- `count_connected_by_type(entities) -> dict`: Returns `{"house": X, "school": Y, "hospital": Z}`.
- `calculate_population_score(saved_people) -> int`: `saved_people * config.POINTS_PER_PERSON`.
- `calculate_efficiency_bonus(remaining_sandbags, all_saved) -> int`: 
    - If `all_saved` is `False` $\rightarrow$ return 0.
    - If `remaining_sandbags < 0` $\rightarrow$ raise `ValueError`.
    - Otherwise $\rightarrow$ `remaining_sandbags * config.EFFICIENCY_BONUS_PER_SANDBAG`.
- `calculate_final_score(population_score, efficiency_bonus) -> int`: Sum of both.
- `is_level_passed(entities) -> bool`: Returns `True` if `count_unsaved_people(entities) == 0`. Raises `ValueError` if only the shelter exists.
- `build_score_breakdown(grid, entities, total_budget) -> dict`: Coordinates all calls. Returns a dictionary with exactly these keys:
    - `"total_population"`
    - `"saved_people"`, `"unsaved_people"`
    - `"houses_connected"`, `"schools_connected"`, `"hospitals_connected"`
    - `"sandbags_allocated"`, `"sandbags_used"`, `"sandbags_remaining"`
    - `"population_score"`, `"efficiency_bonus"`, `"final_score"`
    - `"passed"`

### 3. Weight Management in `scoring.py`
To ensure weights can be changed during testing (e.g., via `monkeypatch`), `scoring.py` will import the `config` module and access constants as attributes:
`score = saved_people * config.POINTS_PER_PERSON`
This allows tests to modify `config.POINTS_PER_PERSON` and see the results reflected in the function calls.

### 4. The "Not Evaluated Yet" Check
The `check_evaluated` function serves as a guard. It is called at the start of `build_score_breakdown`. It loops through all entities; if it finds any building (non-shelter) where `connected` is still `None` (the initial state from `entities.py`), it raises a `ValueError`. This prevents scoring before `pathfinding.evaluate_connectivity` has run.

### 5. Bonus Condition and Testing
The efficiency bonus is strictly conditional on the level being passed (D7).
- **Application**: Inside `build_score_breakdown`, `all_saved` is set to the result of `is_level_passed(entities)`. This boolean is passed to `calculate_efficiency_bonus`.
- **Testing**: 
    - **Passed**: 20/20 saved $\rightarrow$ Bonus = `remaining * weight`.
    - **Failed**: 19/20 saved $\rightarrow$ Bonus = 0.
    - **Empty**: All sandbags used, but all saved $\rightarrow$ Bonus = 0.

### 6. Testing Plan (`tests/test_scoring.py`)
- **Precondition**: `build_score_breakdown` raises `ValueError` if `connected` flags are `None`.
- **Zero Case**: No one connected $\rightarrow$ population score 0, bonus 0, passed False.
- **Perfect Case**: Everyone connected $\rightarrow$ pop score max, bonus > 0, passed True.
- **Partial Case**: Some connected $\rightarrow$ pop score partial, bonus 0, passed False.
- **Type Counts**: Verify `count_connected_by_type` contains all three keys, even if 0.
- **Invariants**:
    - `saved + unsaved == total_population`
    - `used + remaining == allocated`
    - `final == pop_score + bonus`
- **Old SPEC Case**: 20 total, 16 saved, 15/20 used $\rightarrow$ pop 80, bonus 0, final 80, passed False.
- **Monkeypatching**: Change `POINTS_PER_PERSON` to 10 and verify population score doubles.
- **Immutability**: Compare `grid` and `entities` copies before and after `build_score_breakdown`.

### 7. Ambiguities and Conflicts
- **D5 vs SPEC**: D5 explicitly states the bonus is only for passed levels. The plan follows D5, overriding the SPEC example.

### 8. Risks
- **Shelter Handling**: Accidentally counting the shelter in `total_population` or `is_level_passed`. All functions will explicitly skip entities of type `CELL_SHELTER`.
- **Division/Rounding**: Not an issue here as all weights and populations are integers.
