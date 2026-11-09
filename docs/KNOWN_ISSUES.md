# Flood Rescue - Known Issues & Design Limitations

This document catalogs genuine remaining issues, architectural trade-offs, and intentional design limitations of the "Flood Rescue" project as of Feature F12.

---

## 1. Intentional Design Limitations (By Architectural Choice)

### Issue 1: Linear Column Sweep vs Physical Fluid Simulation
- **Description**: The flood animation progresses strictly from left to right, column-by-column across the 30 grid columns, rather than simulating realistic 2D fluid dynamics, water elevation contours, or terrain elevation.
- **Impact**: Flood progression is visual-only and does not flow organically around obstacles.
- **Reason for Choice**: Per SPEC Section 6 and Section 16.D, the flood animation is purely a visual dramatization that plays back the underlying algorithmic outcome. Real-time 2D Navier-Stokes or cellular hydraulic simulation would introduce immense computational overhead and complexity unsuitable for an introductory Computational Thinking course.

### Issue 2: Greedy BFS Baseline Is an Upper Bound (Not Minimum Steiner Tree)
- **Description**: The sandbag budget calculation uses a greedy multi-source Breadth-First Search to connect the nearest building at each step.
- **Impact**: The calculated baseline route is an upper bound on the true minimum number of sandbags, rather than an exact minimum Steiner tree.
- **Reason for Choice**: Finding the exact minimum number of grid cells required to interconnect multiple fixed terminals is the **Rectilinear Steiner Tree problem**, which is NP-hard. Implementing an exponential branch-and-bound or complex geometric approximation is beyond the scope of introductory programming. The greedy BFS heuristic produces intuitive, high-quality shared trunks in $O(V+E)$ time.

### Issue 3: Absence of Mid-Level Menu or Pause Button
- **Description**: During active level planning and route construction, there is no in-game pause button or button to return to the Main Menu. The player can only return to the menu after concluding the campaign in the Final Summary phase, or quit the application via `ESC` / window close.
- **Impact**: Players cannot abort a campaign mid-puzzle back to the title screen without relaunching.
- **Reason for Choice**: Keeping the game phase transition table strictly linear (`planning` $\rightarrow$ `confirming` $\rightarrow$ `flooding` $\rightarrow$ `results`) eliminates intermediate edge-case states, prevents mutable state corruption, and simplifies the state machine for student explanation.

### Issue 4: No Persistent Disk Save or Campaign Resumption
- **Description**: Campaign state lives exclusively in memory and is discarded when the application window closes.
- **Impact**: Players must complete all 3 levels in a single gaming session.
- **Reason for Choice**: File serialization (e.g. JSON or pickle disk saves) was deliberately excluded to keep the codebase focused on core in-memory algorithms, data structures, and game logic without filesystem permission or path-handling edge cases.

---

## 2. Upstream Library Warnings

### Issue 5: Pygame `pkg_resources` Deprecation Warning
- **Description**: On Python 3.12, running tests or starting the game can emit a warning:
  ```
  UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html.
  The pkg_resources package is slated for removal as early as 2025-11-30.
  ```
- **Impact**: Non-fatal warning emitted to console or test runners. Zero effect on game execution or test results.
- **Reason Left Unchanged**: This warning originates internally inside the third-party `pygame` binary package (`pygame/pkgdata.py`) which imports deprecated `setuptools` internals. It cannot be altered from user code without monkeypatching upstream libraries. It will be resolved when the Pygame community releases an updated build targeting newer Python releases.

