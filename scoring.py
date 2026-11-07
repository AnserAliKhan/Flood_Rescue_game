"""
Scoring module.
Calculates population scores, efficiency bonuses, and overall level results.
Pure logic: NO pygame imports allowed.
"""
import config
import sandbags

def check_evaluated(entities):
    """
    Raises ValueError if any non-shelter entity has not been evaluated for connectivity.
    Example: check_evaluated(entities) -> None
    """
    for e in entities:
        if e["type"] != config.CELL_SHELTER and e["connected"] is None:
            raise ValueError("Connectivity has not been evaluated")

def count_saved_people(entities):
    """
    Sums the population of all entities successfully connected to the shelter.
    Example: count_saved_people(entities) -> 16
    """
    return sum(e["population"] for e in entities if e["type"] != config.CELL_SHELTER and e["connected"] is True)

def count_unsaved_people(entities):
    """
    Sums the population of all entities NOT connected to the shelter.
    Example: count_unsaved_people(entities) -> 4
    """
    return sum(e["population"] for e in entities if e["type"] != config.CELL_SHELTER and e["connected"] is False)

def count_connected_by_type(entities):
    """
    Counts connected buildings per type.
    Returns: {'house': X, 'school': Y, 'hospital': Z}
    """
    counts = {"house": 0, "school": 0, "hospital": 0}
    for e in entities:
        t = e["type"]
        if t in counts and e["connected"] is True:
            counts[t] += 1
    return counts

def calculate_population_score(saved_people):
    """
    Calculates score based on people saved.
    Example: calculate_population_score(16) -> 80
    """
    return saved_people * config.POINTS_PER_PERSON

def calculate_efficiency_bonus(remaining_sandbags, all_saved):
    """
    Calculates bonus for unused sandbags, ONLY if all people are saved.
    Example: calculate_efficiency_bonus(5, True) -> 25
    """
    if remaining_sandbags < 0:
        raise ValueError("Remaining sandbags cannot be negative")

    if not all_saved:
        return 0

    return remaining_sandbags * config.EFFICIENCY_BONUS_PER_SANDBAG

def calculate_final_score(population_score, efficiency_bonus):
    """
    Calculates the sum of population score and efficiency bonus.
    Example: calculate_final_score(80, 25) -> 105
    """
    return population_score + efficiency_bonus

def is_level_passed(entities):
    """
    Returns True only if all people in the level were saved.
    Raises ValueError if no buildings are present.
    """
    buildings = [e for e in entities if e["type"] != config.CELL_SHELTER]
    if not buildings:
        raise ValueError("No buildings present in level")

    return count_unsaved_people(entities) == 0

def build_score_breakdown(grid, entities, total_budget):
    """
    Coordinates all scoring functions and returns a comprehensive result record.
    Example: build_score_breakdown(grid, entities, 40) -> { ... }
    """
    # Guard: Ensure connectivity was evaluated first
    check_evaluated(entities)

    # Basic counts
    saved = count_saved_people(entities)
    unsaved = count_unsaved_people(entities)
    total_pop = sum(e["population"] for e in entities if e["type"] != config.CELL_SHELTER)

    # Building type counts
    connected_types = count_connected_by_type(entities)

    # Sandbag counts (Source of truth: the grid)
    used = sandbags.count_sandbags(grid)
    remaining = total_budget - used

    # Scoring
    passed = is_level_passed(entities)
    pop_score = calculate_population_score(saved)
    bonus = calculate_efficiency_bonus(remaining, passed)
    final = calculate_final_score(pop_score, bonus)

    return {
        "total_population": total_pop,
        "saved_people": saved,
        "unsaved_people": unsaved,
        "houses_connected": connected_types["house"],
        "schools_connected": connected_types["school"],
        "hospitals_connected": connected_types["hospital"],
        "sandbags_allocated": total_budget,
        "sandbags_used": used,
        "sandbags_remaining": remaining,
        "population_score": pop_score,
        "efficiency_bonus": bonus,
        "final_score": final,
        "passed": passed
    }
