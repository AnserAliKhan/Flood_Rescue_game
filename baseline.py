"""
Baseline Sandbag Calculator.
Implements the greedy shortest-path heuristic to calculate baseline_sandbags,
the number of sandbags guaranteed to connect all buildings to the shelter.
Pure logic: NO pygame imports allowed.
"""
from collections import deque
import copy
from config import CELL_EMPTY, CELL_SHELTER, CELL_SANDBAG, DIRECTIONS
from grid import in_bounds
import pathfinding


def bfs_to_nearest_target(grid, sources, targets):
    """
    Runs a deterministic multi-source BFS starting from all source cells simultaneously.
    Expands through CELL_EMPTY cells in DIRECTIONS order to locate the nearest target.
    Returns (sandbag_cells, reached_target) where sandbag_cells is the list of empty cells
    to pave from the network outward to reached_target. Returns ([], target) if target already
    touches sources (cost 0). Returns None if targets is empty or unreachable.
    Example: bfs_to_nearest_target(grid, {(5, 10)}, {(5, 15)}) -> ([(5, 11), (5, 12), (5, 13), (5, 14)], (5, 15))
    """
    if not targets:
        return None

    rows = len(grid)
    cols = len(grid[0])

    # Step 1: Check for cost-0 building touching the network directly (Decision D3)
    # Iterate through sorted sources and DIRECTIONS for deterministic ordering
    sorted_sources = sorted(sources)
    for sr, sc in sorted_sources:
        for dr, dc in DIRECTIONS:
            nr, nc = sr + dr, sc + dc
            if in_bounds(nr, nc, rows, cols) and (nr, nc) in targets:
                return ([], (nr, nc))

    # Step 2: Multi-source BFS through CELL_EMPTY cells
    queue = deque(sorted_sources)
    visited = set(sources)
    parent = {}  # maps (r, c) -> predecessor (r, c)

    while queue:
        curr = queue.popleft()
        cr, cc = curr

        for dr, dc in DIRECTIONS:
            nr, nc = cr + dr, cc + dc
            if not in_bounds(nr, nc, rows, cols):
                continue

            # Target reached!
            if (nr, nc) in targets:
                # Reconstruct path from curr backwards until reaching a source cell
                sandbag_cells = []
                node = curr
                while node not in sources:
                    sandbag_cells.append(node)
                    node = parent[node]
                sandbag_cells.reverse()  # Order from network outward
                return (sandbag_cells, (nr, nc))

            # Expand into unvisited empty cells
            if grid[nr][nc] == CELL_EMPTY and (nr, nc) not in visited:
                visited.add((nr, nc))
                parent[(nr, nc)] = curr
                queue.append((nr, nc))

    return None


def calculate_baseline_route(grid, entities):
    """
    Executes the greedy shortest-path heuristic (Decision D2):
    Starts with network = {shelter_cell} and unconnected = {all building cells}.
    Repeatedly connects the nearest unconnected building to the expanding network.
    Returns the ordered list of all newly paved sandbag cells (shared sections counted once).
    Raises ValueError if no shelter exists or if grid already contains any sandbag cells.
    Raises RuntimeError if any building remains unreachable.
    Example: calculate_baseline_route(grid, entities) -> [(5, 11), (5, 12), (5, 13), (5, 14)]
    """
    # 1. Validation
    shelters = [e for e in entities if e["type"] == CELL_SHELTER]
    if len(shelters) != 1:
        raise ValueError(f"Expected exactly 1 shelter, got {len(shelters)}")
    shelter = shelters[0]

    for row in grid:
        if CELL_SANDBAG in row:
            raise ValueError("Baseline must be calculated on an unpaved grid without sandbags.")

    # 2. State setup
    network = {(shelter["row"], shelter["col"])}
    unconnected = {(e["row"], e["col"]) for e in entities if e["type"] != CELL_SHELTER}
    route = []

    # 3. Greedy loop
    while unconnected:
        result = bfs_to_nearest_target(grid, network, unconnected)
        if result is None:
            raise RuntimeError(f"Unreachable building(s) encountered during baseline calculation: {unconnected}")

        new_sandbags, reached_target = result

        # Add newly paved sandbags to route and network
        for cell in new_sandbags:
            if cell not in network:
                route.append(cell)
                network.add(cell)

        # Reached building joins network (can act as relay for subsequent paths, Decision D3)
        network.add(reached_target)
        unconnected.remove(reached_target)

    return route


def calculate_baseline_sandbags(grid, entities):
    """
    Returns the total number of sandbags in the baseline route.
    Equivalent to len(calculate_baseline_route(grid, entities)).
    Example: calculate_baseline_sandbags(grid, entities) -> 4
    """
    return len(calculate_baseline_route(grid, entities))


def calculate_sandbag_budget(baseline):
    """
    Calculates the total level sandbag budget using Decision D2: baseline + SANDBAG_MARGIN.
    Raises ValueError if baseline is negative.
    Example: calculate_sandbag_budget(4) -> 9  (since SANDBAG_MARGIN is 5)
    """
    if baseline < 0:
        raise ValueError(f"Baseline sandbags cannot be negative: {baseline}")
    import config
    return baseline + config.SANDBAG_MARGIN


def route_connects_everything(grid, entities, route):
    """
    Verification helper: creates copies of grid and entities, places sandbags on route cells,
    evaluates connectivity via pathfinding.evaluate_connectivity, and checks if all non-shelter
    buildings are connected. Leaves the original grid and entities completely unchanged.
    Example: route_connects_everything(grid, entities, route) -> True
    """
    grid_copy = copy.deepcopy(grid)
    entities_copy = copy.deepcopy(entities)

    for r, c in route:
        grid_copy[r][c] = CELL_SANDBAG

    pathfinding.evaluate_connectivity(grid_copy, entities_copy)

    for e in entities_copy:
        if e["type"] != CELL_SHELTER and e.get("connected") is not True:
            return False

    return True

