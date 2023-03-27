# Atlasan | Changing Dimensionality of Maps for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

Fix bugs :D <sup>1, 2</sup>

**Processing** <sup>1</sup>
* Create unique identifier for each name for navigation
* Detect text-wrapping
* Remove incorrect room names by looking at nearby room names and see if it is likely to be located there

**Navigation**
* Multi-floor pathfinding <sup>2</sup>
    * Sync up floors to match based on stairs
* Replace hard-coded values <sup>2</sup>
* Update pathfinding <sup>1</sup>
    * Don't let it hug walls

**User-Interface**
* Render staircases & elevators <sup>2</sup>
* Render entire building <sup>2</sup>
* Add indoor-lighting <sup>2</sup>
* Update upload / capture page layout & CSS <sup>1</sup>

## Future Ideas
* Add automatic stairway detection (ones represented by striped lines)
* Find multiple possible paths
* Improve detection accuracy
    * Detect room names that are vertically-oriented
* Generate specific directions based on path