"""
Level generator module.
Creates reproducible, solvable levels with houses, schools, hospitals, and a shelter.
Pure logic: NO pygame imports allowed.
"""
import random
from config import (
    ROWS, COLS, CELL_EMPTY, CELL_SHELTER, DIRECTIONS,
    LEVEL_BUILDINGS, LEVEL_POPULATION, LEVEL_SEEDS, LEVEL_REGIONS,
    POPULATION, MAX_PLACEMENT_TRIES, MAX_LEVEL_RESTARTS
)
from grid import create_grid, in_bounds
from entities import place_entity, count_buildings, total_population


def get_level_composition(level):
    """
    Returns the building-count dictionary for the requested level.
    Validates level exists and total population matches LEVEL_POPULATION[level].
    Raises ValueError for unknown level or population mismatch.
    Example: get_level_composition(1) -> {'house': 5, 'school': 2, 'hospital': 0}
    """
    if level not in LEVEL_BUILDINGS:
        raise ValueError(f"Unknown level: {level}")

    composition = dict(LEVEL_BUILDINGS[level])

    # Verify that population totals match LEVEL_POPULATION
    calc_pop = sum(composition.get(b_type, 0) * POPULATION[b_type] for b_type in composition)
    expected_pop = LEVEL_POPULATION.get(level)
    if calc_pop != expected_pop:
        raise ValueError(
            f"Level {level} composition population ({calc_pop}) does not match expected ({expected_pop})"
        )

    return composition


def build_placement_order(composition):
    """
    Returns a list of building type names in a fixed order (houses, schools, hospitals).
    Placing scarcer buildings in a fixed sequence ensures reproducible generation.
    Example: build_placement_order({'house': 2, 'school': 1, 'hospital': 0}) -> ['house', 'house', 'school']
    """
    order = []
    for b_type in ("house", "school", "hospital"):
        count = composition.get(b_type, 0)
        order.extend([b_type] * count)
    return order


def neighbors_are_free(grid, row, col):
    """
    Returns True if all 4 orthogonal neighbors (DIRECTIONS) are either empty or out of bounds.
    Used for the MIN_BUILDING_GAP spacing constraint (diagonal touching is allowed).
    Example: neighbors_are_free(grid, 5, 5) -> True
    """
    num_rows = len(grid)
    num_cols = len(grid[0])

    for dr, dc in DIRECTIONS:
        nr, nc = row + dr, col + dc
        if in_bounds(nr, nc, num_rows, num_cols):
            if grid[nr][nc] != CELL_EMPTY:
                return False
    return True


def is_valid_spot(grid, row, col, col_range, row_range):
    """
    Returns True if (row, col) is inside the grid, falls within the allowed
    column and row ranges, is empty, and has no orthogonal entity neighbors.
    Example: is_valid_spot(grid, 2, 10, (0, 29), (0, 9)) -> True
    """
    num_rows = len(grid)
    num_cols = len(grid[0])

    if not in_bounds(row, col, num_rows, num_cols):
        return False

    col_min, col_max = col_range
    row_min, row_max = row_range
    if not (col_min <= col <= col_max and row_min <= row <= row_max):
        return False

    if grid[row][col] != CELL_EMPTY:
        return False

    return neighbors_are_free(grid, row, col)


def pick_random_spot(grid, rng, col_range, row_range):
    """
    Tries up to MAX_PLACEMENT_TRIES times to pick a random (row, col) within ranges.
    Returns the first valid (row, col) spot found, or None if all tries fail.
    Example: pick_random_spot(grid, rng, (12, 17), (0, 9)) -> (5, 14)
    """
    col_min, col_max = col_range
    row_min, row_max = row_range

    for _ in range(MAX_PLACEMENT_TRIES):
        r = rng.randint(row_min, row_max)
        c = rng.randint(col_min, col_max)
        if is_valid_spot(grid, r, c, col_range, row_range):
            return (r, c)

    return None


def is_level_solvable(grid, entities):
    """
    Checks whether sandbag paths can connect the shelter to every building:
    1. The shelter has at least one empty orthogonal neighbor.
    2. Every building has at least one empty orthogonal neighbor.
    3. Flood-fill over empty cells starting from shelter's empty neighbors reaches
       at least one empty orthogonal neighbor of every building.
    Returns True if all hold, False otherwise. Does not modify grid or entities.
    Example: is_level_solvable(grid, entities) -> True
    """
    num_rows = len(grid)
    num_cols = len(grid[0])

    # Find the shelter entity
    shelter = None
    buildings = []
    for e in entities:
        if e["type"] == CELL_SHELTER:
            shelter = e
        else:
            buildings.append(e)

    if shelter is None:
        return False

    # 1. Shelter must have at least one empty orthogonal neighbor
    shelter_empty_neighbors = []
    for dr, dc in DIRECTIONS:
        nr, nc = shelter["row"] + dr, shelter["col"] + dc
        if in_bounds(nr, nc, num_rows, num_cols) and grid[nr][nc] == CELL_EMPTY:
            shelter_empty_neighbors.append((nr, nc))

    if not shelter_empty_neighbors:
        return False

    # 2. Every building must have at least one empty orthogonal neighbor
    for b in buildings:
        has_empty_neighbor = False
        for dr, dc in DIRECTIONS:
            nr, nc = b["row"] + dr, b["col"] + dc
            if in_bounds(nr, nc, num_rows, num_cols) and grid[nr][nc] == CELL_EMPTY:
                has_empty_neighbor = True
                break
        if not has_empty_neighbor:
            return False

    # 3. BFS flood-fill over empty cells starting from shelter's empty neighbors
    reachable_empty = set(shelter_empty_neighbors)
    queue = list(shelter_empty_neighbors)

    while queue:
        cr, cc = queue.pop(0)
        for dr, dc in DIRECTIONS:
            nr, nc = cr + dr, cc + dc
            if in_bounds(nr, nc, num_rows, num_cols):
                if grid[nr][nc] == CELL_EMPTY and (nr, nc) not in reachable_empty:
                    reachable_empty.add((nr, nc))
                    queue.append((nr, nc))

    # Every building must have at least one empty neighbor in reachable_empty
    for b in buildings:
        can_reach_building = False
        for dr, dc in DIRECTIONS:
            nr, nc = b["row"] + dr, b["col"] + dc
            if (nr, nc) in reachable_empty:
                can_reach_building = True
                break
        if not can_reach_building:
            return False

    return True


def generate_level(level, seed=None):
    """
    Generates a reproducible, solvable level grid and entities list.
    Uses LEVEL_SEEDS[level] when seed is None.
    Uses an isolated random.Random(seed) instance.
    Retries up to MAX_LEVEL_RESTARTS times if placement or solvability fails.
    Raises RuntimeError if all restarts fail.
    Example: grid, entities = generate_level(1)
    """
    composition = get_level_composition(level)

    if seed is None:
        if level not in LEVEL_SEEDS:
            raise ValueError(f"No default seed configured for level: {level}")
        seed = LEVEL_SEEDS[level]

    rng = random.Random(seed)

    if level not in LEVEL_REGIONS:
        raise ValueError(f"No regions configured for level: {level}")
    regions = LEVEL_REGIONS[level]

    placement_order = build_placement_order(composition)

    for attempt in range(MAX_LEVEL_RESTARTS):
        grid = create_grid(ROWS, COLS)
        entities = []

        # 1. Place Shelter
        shelter_spot = pick_random_spot(
            grid, rng, regions["shelter_cols"], regions["rows"]
        )
        if shelter_spot is None:
            continue
        place_entity(grid, entities, CELL_SHELTER, shelter_spot[0], shelter_spot[1])

        # 2. Place Buildings in fixed order
        failed_placement = False
        for b_type in placement_order:
            spot = pick_random_spot(
                grid, rng, regions["buildings_cols"], regions["rows"]
            )
            if spot is None:
                failed_placement = True
                break
            place_entity(grid, entities, b_type, spot[0], spot[1])

        if failed_placement:
            continue

        # 3. Solvability Check
        if not is_level_solvable(grid, entities):
            continue

        # 4. Final Level Invariants Verification
        actual_counts = count_buildings(entities)
        for b_type, exp_count in composition.items():
            if actual_counts.get(b_type, 0) != exp_count:
                raise ValueError(
                    f"Generated building count mismatch for {b_type}: {actual_counts.get(b_type, 0)} != {exp_count}"
                )

        actual_pop = total_population(entities)
        if actual_pop != LEVEL_POPULATION[level]:
            raise ValueError(
                f"Generated population mismatch: {actual_pop} != {LEVEL_POPULATION[level]}"
            )

        shelters = [e for e in entities if e["type"] == CELL_SHELTER]
        if len(shelters) != 1:
            raise ValueError(f"Expected exactly 1 shelter, got {len(shelters)}")

        return grid, entities

    raise RuntimeError(
        f"Failed to generate solvable level {level} after {MAX_LEVEL_RESTARTS} restarts."
    )

