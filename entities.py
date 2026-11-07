"""
Entities module.
Handles the data model for buildings (houses, schools, hospitals, shelter).
Pure logic: NO pygame imports allowed.
"""
from config import POPULATION, CELL_SHELTER

def create_entity(entity_id, entity_type, row, col):
    """
    Returns a dictionary representing a building entity.
    Example: create_entity(0, 'house', 1, 3) -> {'id': 0, 'type': 'house', ...}
    """
    if entity_type not in POPULATION and entity_type != CELL_SHELTER:
        raise ValueError(f"Unknown entity type: {entity_type}")

    # Shelter population is 0, others come from config
    pop = POPULATION.get(entity_type, 0)

    return {
        "id": entity_id,
        "type": entity_type,
        "row": row,
        "col": col,
        "population": pop,
        "connected": None  # None: not evaluated, True: saved, False: flooded
    }

def place_entity(grid, entities, entity_type, row, col):
    """
    Validates and places an entity on the grid and in the entities list.
    Ensures consistency between the two data structures.
    Example: place_entity(my_grid, my_entities, 'house', 1, 3)
    """
    rows = len(grid)
    cols = len(grid[0])

    # 1. Bounds check
    if not (0 <= row < rows and 0 <= col < cols):
        raise ValueError(f"Position ({row}, {col}) is out of bounds.")

    # 2. Cell must be empty
    if grid[row][col] != "empty":
        raise ValueError(f"Cell at ({row}, {col}) is already occupied.")

    # 3. Shelter check: Only one shelter allowed
    if entity_type == CELL_SHELTER:
        for e in entities:
            if e["type"] == CELL_SHELTER:
                raise ValueError("A shelter already exists on the grid.")

    # Create the entity
    entity_id = len(entities)
    new_entity = create_entity(entity_id, entity_type, row, col)

    # Atomic update to keep consistency
    grid[row][col] = entity_type
    entities.append(new_entity)

    return new_entity

def get_entity_at(entities, row, col):
    """
    Returns the entity dictionary at the given position, or None if empty.
    Example: get_entity_at(entities, 1, 3) -> {'id': 0, ...}
    """
    for e in entities:
        if e["row"] == row and e["col"] == col:
            return e
    return None

def get_entities_by_type(entities, entity_type):
    """
    Returns a list of entities of a specific type.
    Example: get_entities_by_type(entities, 'house')
    """
    return [e for e in entities if e["type"] == entity_type]

def count_buildings(entities):
    """
    Counts houses, schools, and hospitals. Shelter is excluded.
    Example: count_buildings(entities) -> {'house': 6, 'school': 2, 'hospital': 1}
    """
    counts = {"house": 0, "school": 0, "hospital": 0}
    for e in entities:
        t = e["type"]
        if t in counts:
            counts[t] += 1
    return counts

def total_population(entities):
    """
    Sums the population of all entities.
    Example: total_population(entities) -> 30
    """
    return sum(e["population"] for e in entities)

def build_layout(grid, layout):
    """
    Loops over a layout list and places each entity.
    Example: build_layout(grid, [('house', 1, 3), ...])
    """
    entities = []
    for entity_type, row, col in layout:
        place_entity(grid, entities, entity_type, row, col)
    return entities
