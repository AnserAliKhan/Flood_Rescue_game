# Decisions (authoritative: overrides SPEC.md)

## D1. Building combinations (Option B, 2 schools per level, hospital 0/1/2)
| Level | Houses | Schools | Hospitals | Buildings | Population |
|---|---|---|---|---|---|
| 1 | 5 | 2 | 0 | 7 | 10+10+0 = 20 |
| 2 | 6 | 2 | 1 | 9 | 12+10+8 = 30 |
| 3 | 7 | 2 | 2 | 11 | 14+10+16 = 40 |
Level 1 has no hospital. Population totals are fixed and must never be altered.

## D2. Sandbag baseline
"Minimum sandbags" is calculated with a greedy shortest-path heuristic (NOT an exact
Steiner tree): start at the shelter, repeatedly BFS from the current network to the
nearest unconnected building, add that path. The result is called baseline_sandbags
and is an upper bound on the true minimum.
total_sandbags = baseline_sandbags + 5 for ALL levels (same margin, no per-level change).

## D3. Buildings and connectivity
- Adjacent buildings link directly (4-direction only), and a building next to the
  shelter needs 0 sandbags.
- Connected buildings are part of the network, so one connected building can link
  to the next.
- Routes may pass only through sandbag cells, never "through" a building's cell
  as empty space. Sandbags can never be placed on a building.
- Diagonals never count.

## D4. Retry
Retry keeps the SAME layout (same seed). Each level has a fixed seed in config.

## D5. Scoring (amended)
population_score = saved_people * POINTS_PER_PERSON
efficiency_bonus = remaining_sandbags * EFFICIENCY_BONUS_PER_SANDBAG, but ONLY if ALL
people in the level were saved. If anyone is unsaved, efficiency_bonus = 0.
final_score = population_score + efficiency_bonus
Weight is one configurable constant. Proposed value: 5.
This amendment overrides SPEC 9.2 (its example gives a bonus with 16 of 20 saved; under
this rule that bonus would be 0).

## D6. Difficulty
Difficulty comes ONLY from more people and more buildings (7 -> 9 -> 11).
No shrinking sandbag margin.

## D7. Progression
"Continue to Next Level" appears ONLY if ALL people in the level were saved.
Otherwise only "Retry Level" is available.
Because Continue needs all people saved (D7), the bonus is only ever awarded on a passed level.