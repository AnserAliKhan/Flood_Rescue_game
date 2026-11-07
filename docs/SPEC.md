> NOTE TO CLAUDE CODE: Sections 1, 17 and 18 of this document describe an older
> chat-based workflow ("wait for my approval", "do not write code yet",
> "first response"). They are SUPERSEDED. The workflow is now defined in
> CLAUDE.md. Where this spec conflicts with docs/DECISIONS.md, DECISIONS.md wins.
> Section 16 (design questions) has been answered in DECISIONS.md.

# PROJECT: FLOOD RESCUE
## A Python-Based Grid Game Using Pygame

## 1. YOUR ROLE AND OBJECTIVE

Act as a senior Python game developer, software architect, and technical mentor.

I want to develop a 2D grid-based game in Python called **Flood Rescue**. The game is based on a flood evacuation scenario in which the player must construct efficient evacuation routes using a limited number of sandbags.

The project is intended for a university Computational Thinking course. Therefore, the implementation should demonstrate fundamental programming concepts, including:

- Variables and data types
- Conditional statements
- Loops and nested loops
- Lists and nested lists (2D lists)
- Dictionaries
- Functions
- Recursion
- Basic algorithms and pathfinding
- Random number generation
- Data validation
- Modular programming

The game must have a proper graphical user interface (GUI), not a command-line interface.

Use Python and Pygame for the graphical interface unless you identify a compelling technical reason to recommend an alternative.

IMPORTANT DEVELOPMENT INSTRUCTION:

Do not immediately generate the entire game in one response.

First:
1. Understand the complete game requirements.
2. Identify any logical ambiguities or contradictions.
3. Propose a detailed game architecture.
4. Explain how the grid, entities, sandbags, flood simulation, pathfinding, and scoring will work.
5. Break the implementation into small, manageable development stages.
6. Identify which Python concepts will be used in each stage.
7. Wait for my approval before beginning implementation.

I am a beginner-to-intermediate Python student. Explain the reasoning behind implementation decisions and avoid unnecessary complexity.

---

# 2. GENERAL GAME DESCRIPTION

Flood Rescue is a three-level game.

The game contains a rectangular grid consisting of:

- 30 columns
- 10 rows
- 300 individual cells

The grid represents an area that is about to be flooded.

Within the grid, there are several buildings:

1. Houses
2. Schools
3. Hospitals
4. One designated shelter

Each building contains a specific number of people who need to be evacuated.

The player is given a limited number of sandbags.

The player's objective is to strategically place sandbags on empty grid cells to construct connected evacuation routes between the buildings and the designated shelter.

Once the player finishes constructing the routes and confirms their arrangement, the flood simulation begins.

The game then checks which buildings are successfully connected to the shelter through the sandbag network.

People in successfully connected buildings are considered saved.

People in buildings that cannot reach the shelter are considered unsaved.

The game calculates the final score based on:

- Number of people successfully saved.
- Number of sandbags remaining unused.

The game contains three increasingly difficult levels.

---

# 3. GRID DESIGN AND VISUAL REPRESENTATION

## 3.1 Grid dimensions

Every level must contain a grid of exactly 30 columns and 10 rows.

The grid must be displayed prominently in the middle of the game window.

Each cell must be a square with equal width and height.

The cells must have visible boundaries so that the player can clearly distinguish individual positions.

Use a coordinate system consisting of rows and columns.

For example:

- Top-left cell: (0, 0)
- Cell immediately to its right: (0, 1)
- Cell immediately below it: (1, 0)
- Bottom-right cell: (9, 29)

Internally, represent the grid using a two-dimensional Python list.

For example, the grid should conceptually behave like:

    grid[row][column]

The grid must contain 300 individual cells.

The graphical representation must always correspond to the underlying Python data structure.

Do not create the visual grid independently of the actual game data.

## 3.2 Recommended graphical layout

Use a landscape-oriented game window.

Suggested initial window dimensions:

- Width: approximately 1200 pixels.
- Height: approximately 750 pixels.

The screen should be divided into three main sections.

### A. Top information panel

Display:

- Game title: FLOOD RESCUE
- Current level (Level 1, Level 2, or Level 3).
- Remaining sandbags.
- Total number of people in the level.
- Number of buildings.
- Current game phase.

### B. Main grid

The grid should occupy most of the screen.

All 300 cells must be visible simultaneously.

The grid should be positioned centrally.

Every cell must be clickable.

The player should be able to distinguish between different types of cells through colours and, preferably, small icons or letters.

### C. Bottom control panel

Include:

- Sandbag selection tool.
- Confirm/OK button.
- Reset button.
- Instructions.
- Other necessary game controls.

After the flood simulation, use this area to display results or provide a button to continue to the next level.

## 3.3 Cell types and colour coding

Every cell must represent one of the following states:

| Cell type | Suggested colour | Meaning |
|---|---|---|
| Empty cell | Light grey/white | Available for sandbag placement |
| House | Brown/orange | Residential building |
| School | Yellow | Educational building |
| Hospital | Blue | Medical building |
| Shelter | Green | Designated evacuation destination |
| Sandbag | Dark brown/grey | Player-placed protective route |
| Flooded cell | Blue/cyan | Flooded area |
| Safe/connected building | Green highlight | Building successfully connected |
| Unsafe building | Red highlight | Building not successfully connected |

Use clear visual differences between all cell types.

Buildings must never be overwritten by sandbags.

The shelter must have a unique colour and must remain identifiable throughout the game.

Use visual symbols where appropriate:

- H = House
- S = School
- + = Hospital
- SH = Shelter
- B = Sandbag

These symbols are examples. You may use appropriate graphical icons instead if they improve the appearance.

## 3.4 Example of the grid

The following is a conceptual example of a small section of the actual 30 × 10 grid.

    .  .  .  .  .  .  .  .  .  .
    .  H  .  .  .  B  B  .  .  .
    .  .  .  S  .  .  B  .  .  .
    .  .  .  .  .  .  B  .  +  .
    .  .  B  B  B  B  B  .  .  .
    .  .  .  .  .  .  .  .  .  .
    .  +  .  .  .  .  .  .  .  .
    .  .  .  .  .  .  .  .  .  .
    .  .  .  .  .  .  .  SH .  .
    .  .  .  .  .  .  .  .  .  .

Legend:

- H = House
- S = School
- + = Hospital
- SH = Shelter
- B = Sandbag
- . = Empty cell

This is only an illustration of the grid's appearance and possible layout. The actual game must use all 30 columns and 10 rows.

---

# 4. BUILDINGS AND POPULATION DISTRIBUTION

There are four important entity types in the game.

## 4.1 Houses

Each house contains exactly 2 people.

Each house must be represented as a distinct entity.

## 4.2 Schools

Each school contains exactly 5 people.

## 4.3 Hospitals

Each hospital contains exactly 8 people.

## 4.4 Shelter

There will be one designated shelter in each level.

The shelter is the final destination for all evacuation routes.

It must have a unique colour and must be distinguishable from all other buildings.

The shelter should not be counted as an additional population-bearing building unless a separate shelter population is explicitly introduced.

## 4.5 Population requirements

The total population for each level is:

| Level | Total population |
|---|---:|
| Level 1 | 20 people |
| Level 2 | 30 people |
| Level 3 | 40 people |

The population distribution must respect the following rules:

- Each house contains 2 people.
- Each school contains 5 people.
- Each hospital contains 8 people.

The number of hospitals should increase relative to the number of houses as the difficulty increases.

For example, Level 1 should have fewer hospitals than Level 2, and Level 2 should have fewer hospitals than Level 3.

IMPORTANT:

The generator must ensure that the sum of all building populations equals the required level population.

Do not randomly generate an arbitrary number of buildings and then assume that the population will match.

Instead, calculate valid combinations of houses, schools, and hospitals that produce the required population totals.

The following equation must always hold:

    (Number of houses × 2)
    + (Number of schools × 5)
    + (Number of hospitals × 8)
    = Total level population

If the requested population totals and difficulty distribution create a mathematical conflict, explain the conflict and propose valid building combinations before implementation.

Do not silently change the population values.

---

# 5. THREE LEVELS AND DIFFICULTY PROGRESSION

The game must have three levels.

All three levels use the same grid dimensions: 30 × 10.

However, their layouts and difficulty should differ.

## LEVEL 1: EASY

Total population: 20 people.

Characteristics:

- Relatively fewer buildings.
- Fewer hospitals.
- Buildings should be distributed in a relatively manageable arrangement.
- The shelter should be placed in a position that allows relatively straightforward route construction.
- The efficient evacuation route should be comparatively easy to identify.
- The player should have enough room to experiment with sandbag placement.

The purpose of this level is to introduce the game mechanics.

## LEVEL 2: MEDIUM

Total population: 30 people.

Characteristics:

- More buildings than Level 1.
- More hospitals relative to houses.
- Buildings should be distributed across different parts of the grid.
- The shelter should be positioned so that connecting all buildings requires more strategic planning.
- The efficient route should be harder to identify.
- The player should have more complicated route decisions.

## LEVEL 3: HARD

Total population: 40 people.

Characteristics:

- The highest number of people.
- More hospitals relative to houses.
- Buildings should be distributed across a larger portion of the grid.
- The player should need to think carefully about connecting different groups of buildings.
- The route should require more planning.
- The sandbag budget should still allow a valid solution, but inefficient placement should be penalized through lost opportunities to connect buildings.

## 5.1 Random level generation

Buildings should be randomly placed within the 30 × 10 grid.

However, random generation must follow these constraints:

1. No two buildings can occupy the same cell.
2. The shelter cannot overlap with any building.
3. Buildings must be placed within the grid boundaries.
4. The population requirements must be satisfied.
5. There must be enough available cells for the complete layout.
6. The generated level must have at least one valid solution.
7. The player must be able to connect all buildings to the shelter using the allocated sandbags.

The generator must not create impossible levels.

Use a reproducible random seed during debugging so that a particular level layout can be recreated when necessary.

---

# 6. SANDBAG MECHANICS

This is the central mechanic of the game.

The player receives a predefined number of sandbags at the beginning of each level.

The number of sandbags is calculated by the game itself.

## 6.1 Calculating the sandbag budget

The system must first determine the minimum number of sandbags required to connect all buildings to the shelter.

Call this value:

    minimum_sandbags

The player should receive:

    total_sandbags = minimum_sandbags + 5

Therefore, the player receives five additional sandbags beyond the theoretical minimum.

This gives the player a small margin for experimentation and imperfect decisions.

IMPORTANT:

The minimum sandbag calculation must account for the fact that multiple buildings may share portions of the same evacuation route.

Do not simply calculate the distance from every building to the shelter independently and add all those distances together.

That would incorrectly count shared sections multiple times.

Instead, determine the minimum connected network of sandbag cells that connects all building locations to the shelter.

Treat this as a minimum connected network/pathfinding optimization problem on a grid.

Consider an appropriate algorithm for the problem, such as a Steiner-tree-style approximation or another suitable approach.

Explain the algorithm and its limitations before implementation.

The solution must be practical for a 30 × 10 grid and appropriate for a university-level Python project.

The calculated sandbag budget must always permit at least one valid solution.

## 6.2 Selecting sandbags

The user interface must provide a visible sandbag selection tool.

The player should:

1. Click the sandbag tool.
2. Click an empty cell on the grid.
3. The selected cell becomes a sandbag.
4. The remaining sandbag counter decreases by one.

The player should be able to repeat this process until the available sandbags are exhausted or they decide to confirm their arrangement.

## 6.3 Permitted placement directions

Sandbags can only connect through four directions:

- Up
- Down
- Left
- Right

Diagonal connections are strictly prohibited.

For example:

If a sandbag occupies position (3, 4), its permitted neighbouring positions are:

- (2, 4)
- (4, 4)
- (3, 3)
- (3, 5)

Positions such as (2, 3) or (4, 5) must not count as connected.

Use this same four-direction rule in every part of the game's pathfinding and connectivity calculations.

## 6.4 Placement restrictions

The player must not be able to:

- Place sandbags outside the grid.
- Place sandbags on houses.
- Place sandbags on schools.
- Place sandbags on hospitals.
- Place sandbags on the shelter.
- Place more sandbags than the allocated budget.

The player should also be able to remove a previously placed sandbag before confirming the arrangement.

When a sandbag is removed, the available sandbag counter should increase accordingly.

The grid must visually update whenever a sandbag is placed or removed.

---

# 7. PLANNING PHASE AND CONFIRMATION

At the beginning of every level, the game enters the planning phase.

During this phase:

- The grid is visible.
- Buildings are visible.
- The shelter is visible.
- The sandbag budget is displayed.
- The player can place and remove sandbags.
- The game must not begin the flood simulation automatically.

The player can experiment with different routes.

Once satisfied, the player clicks a button labelled:

    CONFIRM ROUTES / START FLOOD

After clicking this button:

1. Stop accepting sandbag placement.
2. Validate the grid.
3. Begin the flood simulation.
4. Calculate which buildings are connected to the shelter.
5. Calculate how many people were saved.
6. Calculate how many people were not saved.
7. Calculate the final score.

Include a confirmation message if necessary so the player does not accidentally start the flood.

---

# 8. FLOOD SIMULATION AND EVACUATION LOGIC

The flood simulation is the stage where the game evaluates the player's decisions.

The backend must determine whether each building has a valid route to the shelter.

## 8.1 Definition of a valid evacuation route

A building is considered connected to the shelter if there exists a continuous path from that building to the shelter.

The path must follow these rules:

1. The path can move horizontally or vertically.
2. Diagonal movement is prohibited.
3. Every intermediate cell must contain a player-placed sandbag.
4. Buildings and the shelter can act as the endpoints of the path.
5. A building is successfully connected if it can reach the shelter through the connected sandbag network.

Multiple buildings may share the same sandbag route.

This is important because the player should be encouraged to build an efficient shared network instead of independent routes for every building.

The connectivity system should evaluate the complete network, not just individual sandbags in isolation.

## 8.2 Flood evaluation

Once the player confirms the routes, the game should simulate the flood.

The actual flood animation can be visual, but the fundamental evaluation must be based on the connectivity rules above.

A simple and reliable implementation is acceptable initially:

- Buildings connected to the shelter through the sandbag network are safe.
- Buildings without a valid connection are considered flooded/unsafe.

Use the four-direction connectivity rule consistently.

The flood simulation should visually communicate the result.

For example:

- Successfully connected buildings can turn green.
- Unconnected buildings can turn red.
- Empty areas can display a blue flood effect.
- Sandbag routes can remain visually highlighted.

The flood animation must not change the result of the backend connectivity calculation.

The backend must determine the result first, and the animation must display that result.

## 8.3 Pathfinding algorithm

Implement an algorithm to check connectivity between all buildings and the shelter.

Possible approaches:

- Depth-First Search (DFS).
- Breadth-First Search (BFS).
- Recursive flood-fill/pathfinding.

Because this is a Computational Thinking course, I would prefer an implementation that allows me to understand and demonstrate recursion.

However, compare recursive DFS with iterative DFS or BFS and explain which is more appropriate.

The algorithm should:

1. Start from the shelter.
2. Explore neighbouring sandbag cells.
3. Follow only the four permitted directions.
4. Identify every building connected to the shelter.
5. Mark the connected buildings as safe.
6. Mark the remaining buildings as unsafe.

Avoid repeatedly performing unnecessary path searches if one traversal from the shelter can identify all connected buildings.

---

# 9. SCORING SYSTEM

The scoring system must reward both successful evacuation and efficient use of sandbags.

## 9.1 Population score

Every successfully evacuated person earns:

    +5 points

Every person who is not successfully evacuated earns:

    +0 points

The total population score is:

    population_score = saved_people × 5

The maximum possible population scores are:

| Level | Total population | Maximum population score |
|---|---:|---:|
| Level 1 | 20 | 100 |
| Level 2 | 30 | 150 |
| Level 3 | 40 | 200 |

For example:

If Level 1 contains 20 people and the player saves 16:

    population_score = 16 × 5

    population_score = 80

The four unsaved people contribute zero points.

## 9.2 Remaining sandbag bonus

The player should also receive a bonus for conserving sandbags.

The more sandbags that remain unused after the player constructs the routes, the better the player's score should be.

Calculate:

    remaining_sandbags =
        total_sandbags - used_sandbags

Introduce a configurable sandbag-efficiency bonus.

For the initial implementation, use:

    efficiency_bonus = remaining_sandbags × 1

Therefore:

    final_score =
        population_score + efficiency_bonus

Keep the efficiency bonus configurable so that its weight can be adjusted after testing.

## 9.3 Example scoring calculation

Suppose:

- Total population = 20.
- Saved population = 16.
- Total sandbags = 20.
- Used sandbags = 15.
- Remaining sandbags = 5.

Then:

    Population score = 16 × 5 = 80

    Efficiency bonus = 5 × 1 = 5

    Final score = 85

The scoring system should display a clear breakdown rather than just showing one final number.

IMPORTANT:

The population score and the efficiency bonus should be displayed separately.

The maximum population score is 100, 150, or 200 depending on the level. The final score may exceed these values because of the additional efficiency bonus.

---

# 10. RESULTS SCREEN

After the flood simulation, display a results screen.

The screen must include:

- Current level.
- Total population.
- Number of people saved.
- Number of people not saved.
- Number of houses successfully connected.
- Number of schools successfully connected.
- Number of hospitals successfully connected.
- Number of sandbags allocated.
- Number of sandbags used.
- Number of sandbags remaining.
- Population score.
- Sandbag-efficiency bonus.
- Final score.

Also visually distinguish safe and unsafe buildings on the grid.

For example:

    FLOOD RESULTS

    Total Population: 20
    People Saved: 16
    People Not Saved: 4

    Sandbags Allocated: 20
    Sandbags Used: 15
    Sandbags Remaining: 5

    Population Score: 80
    Efficiency Bonus: 5

    FINAL SCORE: 85

Provide two buttons:

1. Retry Level
2. Continue to Next Level

The Continue button should be available when the current level has been completed.

After Level 3, display a final game summary containing the scores achieved in all three levels and the overall score.

---

# 11. USER EXPERIENCE AND GAME FLOW

The game should follow this overall sequence:

SCREEN 1: MAIN MENU

Display:

- Game title.
- Start Game button.
- Instructions button.
- Exit button.

SCREEN 2: LEVEL 1

- Generate the Level 1 grid.
- Display all buildings.
- Display the shelter.
- Display the sandbag budget.
- Allow the user to construct routes.

SCREEN 3: CONFIRMATION

- User clicks Confirm Routes.
- Stop accepting new sandbag placements.
- Validate the arrangement.
- Start flood simulation.

SCREEN 4: FLOOD SIMULATION

- Animate the flood.
- Highlight connected and disconnected buildings.
- Calculate the number of saved and unsaved people.

SCREEN 5: LEVEL RESULTS

- Display the score breakdown.
- Show remaining sandbags.
- Allow the user to retry or continue.

SCREEN 6: LEVEL 2

Repeat the same gameplay with a more difficult grid.

SCREEN 7: LEVEL 3

Repeat the same gameplay with the highest population and difficulty.

SCREEN 8: FINAL RESULTS

Display:

- Level 1 score.
- Level 2 score.
- Level 3 score.
- Total game score.
- Total number of people saved across all levels.
- Overall sandbag efficiency.

Allow the user to restart the game or return to the main menu.

---

# 12. TECHNICAL ARCHITECTURE

Organize the code into logical modules rather than putting everything into one large Python file.

A suggested initial structure is:

    FloodRescue/
    │
    ├── main.py
    │
    ├── game.py
    │
    ├── grid.py
    │
    ├── level_generator.py
    │
    ├── entities.py
    │
    ├── sandbags.py
    │
    ├── pathfinding.py
    │
    ├── flood.py
    │
    ├── scoring.py
    │
    ├── interface.py
    │
    ├── assets/
    │   ├── images/
    │   └── fonts/
    │
    └── README.md

These are proposed responsibilities:

### main.py
Entry point of the program.

Initializes Pygame and starts the game.

### game.py
Controls the overall game flow, levels, and game states.

### grid.py
Creates and manages the 30 × 10 two-dimensional grid.

Handles grid coordinates and cell states.

### level_generator.py
Generates random buildings and the shelter.

Ensures that population totals and placement constraints are respected.

### entities.py
Defines houses, schools, hospitals, and shelters.

Stores their positions and population information.

### sandbags.py
Handles sandbag placement, removal, and budget management.

### pathfinding.py
Contains the connectivity algorithm.

Checks whether buildings can reach the shelter.

### flood.py
Handles the flood simulation and its visual progression.

### scoring.py
Calculates the population score, efficiency bonus, and final score.

### interface.py
Handles Pygame rendering, mouse interaction, buttons, text, and visual components.

You may modify this architecture if you can justify a simpler or more appropriate structure.

Avoid creating unnecessary classes or abstractions just for the sake of using object-oriented programming.

---

# 13. PROGRAMMING CONCEPTS THAT SHOULD BE DEMONSTRATED

This is an academic project, so the code should demonstrate meaningful use of the concepts taught in a beginner Python course.

Prioritize:

### 2D Lists
Represent the 30 × 10 grid.

### Dictionaries
Store entity information, including:

- Entity type.
- Position.
- Population.
- Connection status.

### Nested Loops
Generate and render all 300 cells.

### Functions
Divide the game into understandable operations.

### Recursion
Implement or demonstrate recursive DFS/pathfinding where appropriate.

### Conditional Statements
Validate placement and determine safe/unsafe buildings.

### Random Module
Generate different level layouts.

### Basic Algorithms
Use graph traversal and route optimization.

The implementation should be appropriate for my course level.

Do not introduce advanced frameworks, databases, networking, or unnecessary external dependencies.

Use Pygame and Python's standard library wherever possible.

---

# 14. VISUAL DESIGN REQUIREMENTS

The game should look like a polished 2D strategy/puzzle game.

Avoid making it look like a basic programming exercise.

Design preferences:

- Clean, modern interface.
- Landscape layout.
- Clearly visible grid.
- Consistent colour scheme.
- Distinct building icons.
- Clear sandbag counter.
- Visually appealing buttons.
- Smooth flood animation.
- Clear score presentation.

The grid should remain the primary focus.

Use simple graphical shapes or freely usable assets.

Do not spend excessive time on complex graphics before the core game mechanics work.

Functionality should always take priority over decoration.

---

# 15. TESTING AND VALIDATION

The game must be tested systematically.

At minimum, test the following:

1. Grid contains exactly 300 cells.
2. No building overlaps another building.
3. Exactly one shelter is generated per level.
4. Population totals are correct.
5. The sandbag budget is calculated correctly.
6. Sandbags cannot be placed outside the grid.
7. Sandbags cannot overwrite buildings.
8. Sandbag placement decreases the remaining budget.
9. Removing a sandbag restores the budget.
10. Diagonal connections are not accepted.
11. Valid horizontal connections are accepted.
12. Valid vertical connections are accepted.
13. Buildings connected to the shelter are marked safe.
14. Disconnected buildings are marked unsafe.
15. Population scores are calculated correctly.
16. Efficiency bonuses are calculated correctly.
17. The three levels have increasing difficulty.
18. The game can be restarted without retaining old level data.
19. The flood animation does not interfere with the underlying score calculation.

Use simple test cases for pathfinding before integrating it with the graphical interface.

---

# 16. IMPORTANT DESIGN QUESTIONS THAT MUST BE RESOLVED BEFORE CODING

Before implementation, analyze these issues and present your recommendations.

### A. Minimum sandbag calculation

What is the most appropriate algorithm for calculating the minimum number of sandbags needed to connect every building to the shelter?

Explain how shared paths between buildings will be accounted for.

### B. Level population combinations

Find valid combinations of houses, schools, and hospitals that produce exactly 20, 30, and 40 people while respecting the fixed population values.

Also ensure that the hospital-to-house ratio increases with each level.

### C. Random placement

How can buildings be placed randomly without generating impossible layouts?

### D. Flood simulation

What is the simplest reliable way to represent the flood while ensuring that the connectivity calculation determines the final outcome?

### E. Sandbag efficiency

How should the efficiency bonus be calculated so that players are rewarded for saving people while also conserving sandbags?

### F. Difficulty progression

How can the three levels become progressively harder without making them unfair or impossible?

### G. Recursive pathfinding

How can recursion be used meaningfully in this project without introducing unnecessary complexity?

Present your answers before beginning implementation.

---

# 17. DEVELOPMENT APPROACH

I want to build this project incrementally and understand how it works.

Do not write the entire application at once.

Follow these development stages:

STAGE 1: PROJECT SETUP
- Set up the project directory.
- Create the virtual environment.
- Install Pygame.
- Open a basic Pygame window.

STAGE 2: GRID IMPLEMENTATION
- Create the 30 × 10 grid using nested lists.
- Render all 300 cells.
- Add grid coordinates.
- Make individual cells clickable.
- Demonstrate how screen coordinates translate into grid coordinates.

STAGE 3: BUILDINGS
- Create houses, schools, hospitals, and shelters.
- Display them using different colours and icons.
- Introduce population attributes.

STAGE 4: LEVEL GENERATION
- Implement the three levels.
- Generate valid population distributions.
- Randomly position buildings.
- Ensure every generated level is solvable.

STAGE 5: SANDBAG PLACEMENT
- Add the sandbag selection tool.
- Implement placement and removal.
- Implement the sandbag budget.
- Validate all placement restrictions.

STAGE 6: PATHFINDING
- Implement the minimum connected network calculation.
- Implement DFS/BFS or recursive DFS for connectivity.
- Test all pathfinding cases independently.

STAGE 7: FLOOD SIMULATION
- Add the confirmation button.
- Freeze the grid.
- Evaluate connectivity.
- Animate the flood.
- Highlight safe and unsafe buildings.

STAGE 8: SCORING
- Calculate people saved.
- Calculate people not saved.
- Calculate the sandbag efficiency bonus.
- Display the results.

STAGE 9: GAME PROGRESSION
- Implement all three levels.
- Add retry and continue functionality.
- Implement the final results screen.

STAGE 10: POLISHING AND TESTING
- Improve the UI.
- Add instructions.
- Fix bugs.
- Test different layouts.
- Verify scoring and pathfinding.

At the end of every stage:

1. Explain what was implemented.
2. Explain the important code sections.
3. Explain the Python concepts used.
4. Tell me how to run and test the implementation.
5. Identify any bugs or limitations.
6. Wait for my approval before moving to the next stage.

---

# 18. YOUR FIRST RESPONSE

For now, DO NOT WRITE ANY CODE.

I want your first response to contain:

1. Your understanding of the complete game.
2. A detailed explanation of how the 30 × 10 grid should work.
3. A proposed visual layout for the Pygame interface.
4. A breakdown of the game mechanics.
5. Valid population combinations for all three levels.
6. Your proposed sandbag optimization algorithm.
7. Your proposed pathfinding and flood evaluation algorithms.
8. A suggested project architecture.
9. Any ambiguities or contradictions you identified.
10. A clear, sequential development roadmap.

Explain your decisions in language that a university-level beginner Python student can understand.

Do not make major design decisions silently.

If you believe a requirement should be changed, explain why and ask for my approval.

The ultimate goal is to build a functional, visually appealing, logically correct, and academically explainable Python game that I can confidently demonstrate and explain to my course instructor.

