# Atlasan | Changing Dimensionality of Maps for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

Fix bugs :D ^1^^2^

**Processing** ^1^
* Create unique identifier for each name for navigation
* Detect text-wrapping
* Remove incorrect room names by looking at near-by room names and see if it is likely to be located there

**Navigation**
* Multi-floor pathfinding ^2^
    * Sync up floors to match based on stairs
* Replace hard-coded values ^2^
* Update pathfinding ^1^
    * Don't let it hug walls

**User-Interface**
* Render staircases & elevators ^2^
* Render entire building ^2^
* Add indoor-lighting ^2^
* Update upload / capture page layout & CSS ^1^

## Future Ideas
* Add automatic stairway detection (ones represented by striped lines)
* Find multiple possible paths
* Improve detection accuracy
    * Detect room names that are vertically-oriented
* Generate specific directions based on path