# Session Notes

## Key Decision Context
- **Decision D3 (Connectivity)**: It was decided that buildings can act as relays. If a house is connected to the shelter, any building adjacent to that house is also connected. This simplifies the network and is a key academic demonstration of graph traversal.
- **Decision D5 (Efficiency Bonus)**: The original SPEC allowed a bonus for any remaining sandbags. This was amended to require a "Perfect Clear" (all people saved) to earn the bonus. This adds a layer of strategic difficulty.
- **State Machine**: The transition from Planning $\rightarrow$ Confirming $\rightarrow$ Results was implemented to ensure the user cannot change the grid once they've committed to a result, and to allow for the future addition of a flood animation.

## Implementation Details
- **Coordinate Mapping**: The project uses a `GRID_ORIGIN_X` and `GRID_ORIGIN_Y` to center the 30x10 grid. The `pixel_to_cell` and `cell_to_pixel` functions in `grid.py` are the critical bridge between Pygame's pixel space and the 2D list's index space.
- **Recursive DFS**: The pathfinding uses a recursive approach to demonstrate the "Call Stack" concept for the university project. An iterative version was also implemented in `pathfinding.py` to verify the recursive results.
- **Single Source of Truth**: The budget is not stored as a decreasing counter. Instead, `sandbags.count_sandbags(grid)` is called every frame. This prevents bugs where the counter and the actual number of sandbags on screen disagree.

## Interactional Context
- The user is a beginner-to-intermediate student. All code is written to be explainable.
- We have strictly followed a spec-driven workflow: reading the feature file, writing a plan, implementing, and then verifying with pytest before moving to the next feature.
