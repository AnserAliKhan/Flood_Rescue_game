"""
Campaign module.
Manages multi-level campaign progression, level preparation,
score recording, level completion routing, and final summary building.
Pure logic: NO pygame imports allowed.
"""
import copy
from config import NUM_LEVELS
import level_generator
import baseline
import game


def create_campaign(start_level=1):
    """
    Initializes a new campaign state dictionary.
    Returns {'level': start_level, 'level_results': {}}.
    Raises ValueError if start_level not in 1..NUM_LEVELS.
    Example: create_campaign() -> {'level': 1, 'level_results': {}}
    """
    if not (1 <= start_level <= NUM_LEVELS):
        raise ValueError(f"start_level must be between 1 and {NUM_LEVELS}, got: {start_level}")

    return {
        "level": start_level,
        "level_results": {}
    }


def prepare_level(level):
    """
    Generates level layout and calculates baseline sandbags and total budget.
    Returns (grid, entities, baseline_sandbags, total_budget).
    Raises ValueError if level not in 1..NUM_LEVELS.
    Example: prepare_level(1) -> (grid, entities, 24, 29)
    """
    if not (1 <= level <= NUM_LEVELS):
        raise ValueError(f"level must be between 1 and {NUM_LEVELS}, got: {level}")

    grid, entities = level_generator.generate_level(level)
    b_sandbags = baseline.calculate_baseline_sandbags(grid, entities)
    budget = baseline.calculate_sandbag_budget(b_sandbags)

    return grid, entities, b_sandbags, budget


def is_last_level(campaign):
    """
    Returns True if the campaign is currently on the final level (NUM_LEVELS).
    Example: is_last_level({'level': 3, ...}) -> True
    """
    return campaign["level"] == NUM_LEVELS


def is_campaign_complete(campaign):
    """
    Returns True if every level 1..NUM_LEVELS has a stored result in level_results.
    Example: is_campaign_complete(campaign) -> True
    """
    return all(lvl in campaign["level_results"] for lvl in range(1, NUM_LEVELS + 1))


def record_level_result(campaign, breakdown):
    """
    Stores a deep copy of breakdown under the current campaign level.
    Raises ValueError if breakdown['passed'] is not True or level was already recorded.
    Example: record_level_result(campaign, breakdown)
    """
    if not breakdown or not breakdown.get("passed"):
        raise ValueError("Cannot record level result: level was not passed")

    lvl = campaign["level"]
    if lvl in campaign["level_results"]:
        raise ValueError(f"Level {lvl} has already been recorded in this campaign")

    campaign["level_results"][lvl] = copy.deepcopy(breakdown)


def complete_level(campaign, state):
    """
    Called when player clicks Continue in results phase.
    Validates game.can_continue(state), records the level result.
    If on final level, returns 'summary'.
    Otherwise advances campaign['level'] by 1 and returns 'next_level'.
    Leaves campaign unchanged on error.
    Example: complete_level(campaign, state) -> 'next_level'
    """
    if not game.can_continue(state):
        raise ValueError("Cannot complete level: game state is not in a valid passed results phase")

    # Record the result for current level
    record_level_result(campaign, state["breakdown"])

    if is_last_level(campaign):
        return "summary"

    campaign["level"] += 1
    return "next_level"


def build_final_summary(campaign):
    """
    Aggregates campaign results into a summary dictionary:
    - 'rows': list of dicts per recorded level in level order.
    - 'total_score': sum of final scores.
    - 'total_people_saved', 'total_population': summed population stats.
    - 'sandbags_allocated', 'sandbags_used', 'sandbags_remaining': summed sandbag stats.
    - 'efficiency_percent': 100 * sandbags_remaining / sandbags_allocated rounded to 1 decimal (0.0 if empty).
    - 'levels_completed': count of recorded levels.
    Works for partial or empty campaign without division by zero.
    Does not modify campaign.
    Example: build_final_summary(campaign) -> {'total_score': 525, ...}
    """
    rows = []
    # Sorted by level number
    for lvl in sorted(campaign["level_results"].keys()):
        b = campaign["level_results"][lvl]
        rows.append({
            "level": lvl,
            "saved_people": b["saved_people"],
            "total_population": b["total_population"],
            "sandbags_used": b["sandbags_used"],
            "sandbags_allocated": b["sandbags_allocated"],
            "population_score": b["population_score"],
            "efficiency_bonus": b["efficiency_bonus"],
            "final_score": b["final_score"],
        })

    total_score = sum(r["final_score"] for r in rows)
    total_saved = sum(r["saved_people"] for r in rows)
    total_pop = sum(r["total_population"] for r in rows)
    total_allocated = sum(r["sandbags_allocated"] for r in rows)
    total_used = sum(r["sandbags_used"] for r in rows)
    total_remaining = total_allocated - total_used

    if total_allocated > 0:
        efficiency_percent = round(100.0 * total_remaining / total_allocated, 1)
    else:
        efficiency_percent = 0.0

    return {
        "rows": rows,
        "total_score": total_score,
        "total_people_saved": total_saved,
        "total_population": total_pop,
        "sandbags_allocated": total_allocated,
        "sandbags_used": total_used,
        "sandbags_remaining": total_remaining,
        "efficiency_percent": efficiency_percent,
        "levels_completed": len(rows),
    }

