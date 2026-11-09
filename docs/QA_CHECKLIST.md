# Flood Rescue - Manual Quality Assurance (QA) Checklist

This manual checklist is designed for human evaluation of all interactive graphical features, controls, and visual states before grading or demonstration.

---

## 1. Application Startup and Main Menu

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Clean Launch** | Run `python main.py`. Window opens sized 1200x750 with title "Flood Rescue". | |
| [ ] | **Menu Rendering** | Main Menu displays title "FLOOD RESCUE", tagline "Build routes. Save everyone.", and 3 buttons. | |
| [ ] | **Button Hovering** | Moving mouse over `START GAME`, `INSTRUCTIONS`, and `EXIT` changes button background brightness. | |
| [ ] | **Menu Exit (Button)** | Clicking `EXIT` closes the window cleanly with zero errors or traceback in terminal. | |
| [ ] | **Menu Exit (ESC)** | Relaunch game, press `ESC` on menu. Window closes cleanly. | |

---

## 2. Instructions Screen

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Screen Navigation** | From Main Menu, click `INSTRUCTIONS`. Instructions screen appears immediately. | |
| [ ] | **Layout & Spacing** | Six distinct sections (Goal, How to Play, Rules, People, Scoring, Levels) formatted into 2 clean columns. | |
| [ ] | **No Line Overflow** | All bullet points fit within their 500px column boundary without overlapping or clipping. | |
| [ ] | **Dynamic Constants** | Section text displays exact values: `5 points`, `5 margin`, `5 points bonus`, `House: 2`, `School: 5`, `Hospital: 8`. | |
| [ ] | **Return via BACK** | Hover and click `BACK` button. Returns smoothly to Main Menu. | |
| [ ] | **Return via ESC** | Open `INSTRUCTIONS` again, press `ESC`. Returns smoothly to Main Menu. | |

---

## 3. Planning Phase & Sandbag Tool

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Level 1 Initialization** | Click `START GAME`. Level 1 loads (Seed 101: 7 buildings, population 20, sandbags: 29/29). | |
| [ ] | **Grid Visuals** | All 300 cells (10 rows x 30 cols) are visible simultaneously with dark gridlines and coordinate numbers. | |
| [ ] | **Building Labels** | Green shelter labeled `SH`, brown houses labeled `H`, yellow schools labeled `S`. | |
| [ ] | **HUD Information** | Top panel displays level title "Easy", running score "0", population "20", and phase "Planning". | |
| [ ] | **Inspection Readout** | Hovering over grid cells updates the `Hover: (r, c)` readout. Hovering over buildings displays entity name & population. | |
| [ ] | **Sandbag Toggle (S key)**| Press `S`. Sandbag tool activates. Button changes color. Press `S` again to deactivate. | |
| [ ] | **Sandbag Toggle (Button)**| Click `SANDBAG TOOL` button. Tool activates. Click again to deactivate. | |
| [ ] | **Valid Sandbag Placement**| Activate tool. Left-click empty cells. Dark grey sandbag `B` appears, counter decreases by 1. | |
| [ ] | **Sandbag Budget Limit** | Place sandbags until budget reaches 0/29. Attempting another placement displays error message. | |
| [ ] | **Occupied Cell Protection**| Attempt to place sandbag on a house, school, or shelter. Placement rejected with feedback. | |
| [ ] | **Sandbag Removal (Left-click)**| Left-click an existing sandbag with tool active. Sandbag removed, counter increases by 1. | |
| [ ] | **Sandbag Removal (Right-click)**| Right-click an existing sandbag. Sandbag removed immediately without requiring tool mode. | |
| [ ] | **Grid Reset Button** | Place several sandbags. Click `RESET`. All sandbags cleared, counter resets to 29/29, message says "Grid reset." | |

---

## 4. Route Confirmation & Dialog

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Confirm Routes Trigger** | Click `CONFIRM ROUTES / START FLOOD`. Modal dialog appears with darkened transparent overlay. | |
| [ ] | **Dialog Counter Readout**| Dialog reports correct number of sandbags remaining. | |
| [ ] | **Keep Planning (Button)**| Click `KEEP PLANNING`. Dialog dismisses, returns to Planning phase with placed sandbags intact. | |
| [ ] | **Keep Planning (ESC)** | Click confirm again, then press `ESC`. Dialog dismisses safely. | |

---

## 5. Flood Animation Phase

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Flood Animation Sweep** | From dialog, click `START FLOOD`. Water wave progresses column-by-column from left to right across 30 columns. | |
| [ ] | **Leading Wave Highlight**| The front column displays a brighter blue leading edge. | |
| [ ] | **Flooded Building Marker**| Disconnected buildings reached by water receive a red outline. | |
| [ ] | **Skip Animation (SPACE)**| Run flood and press `SPACE`. Animation immediately finishes and transitions to Results phase. | |
| [ ] | **Skip Animation (Click)**| Run flood and left-click anywhere. Animation immediately skips to Results phase. | |

---

## 6. Results Phase & Progression

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Safe / Unsafe Outlines**| Connected buildings outlined in bright green; unconnected buildings outlined in red. | |
| [ ] | **Results Breakdown** | Bottom panel shows: Saved / Unsaved, Buildings connected, Sandbags used/remaining, Population score, Bonus, Final score. | |
| [ ] | **Efficiency Bonus (Passed)**| When all 20 civilians are saved, bonus equals `remaining * 5`. Message states bonus awarded. | |
| [ ] | **Efficiency Bonus (Failed)**| Intentionally leave 1 house unconnected. Bonus equals strictly 0. Message explains why. | |
| [ ] | **Conditional Continue** | If level is passed, `CONTINUE TO NEXT LEVEL` button is visible. If level failed, only `RETRY LEVEL` appears. | |
| [ ] | **Retry Level** | Click `RETRY LEVEL`. State resets to Planning on Level 1. Layout is identical; sandbags cleared. | |
| [ ] | **Level 2 Progression** | Pass Level 1 and click `CONTINUE`. Level 2 (Medium) loads: 9 buildings, 30 pop, budget 39, includes blue Hospital (`+`). | |
| [ ] | **Level 3 Progression** | Pass Level 2 and click `CONTINUE`. Level 3 (Hard) loads: 11 buildings, 40 pop, budget 40, includes 2 Hospitals. | |

---

## 7. Campaign Summary & Restart

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Summary Screen Trigger** | Complete Level 3 with all civilians saved. Continue button label reads `VIEW FINAL SUMMARY`. Click it. | |
| [ ] | **Summary Table** | Full-screen table displays rows for Level 1, 2, and 3 with Saved/Total, Sandbags used, Pop score, Bonus, and Level score. | |
| [ ] | **Aggregate Statistics** | Highlights Total Score, Total People Saved (e.g., 90/90), Sandbags Conserved, and Efficiency %. | |
| [ ] | **Dual Summary Buttons** | `PLAY AGAIN` and `MAIN MENU` buttons appear side-by-side with no overlap and hover response. | |
| [ ] | **Play Again Flow** | Click `PLAY AGAIN`. Level 1 loads with fresh campaign, 0 score, and identical layout. | |
| [ ] | **Main Menu Return** | From summary screen, click `MAIN MENU`. Main Menu appears. Clicking `START GAME` starts a fresh campaign. | |

---

## 8. Repeatability and Determinism (3-Run Comparison)

| Check | Item Description | Verification Steps | Notes / Status |
| :---: | :--- | :--- | :--- |
| [ ] | **Run 1 Layout** | Launch game, note Shelter coordinate on Level 1: `(row 5, col 15)` and first house position. | |
| [ ] | **Run 2 Layout** | Restart game, check Level 1 layout. Exact same coordinates and entities appear. | |
| [ ] | **Run 3 Layout** | Close and relaunch python `main.py`, check Level 1. Exact same layout verified (Deterministic Seed 101). | |

