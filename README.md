# Atlasan | Changing Dimensionality of Maps for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

Fix bugs :D <sup>1, 2</sup>

**Processing** <sup>1</sup>
* Detect text-wrapping

**Navigation**
* Multi-floor pathfinding <sup>2</sup>
    * Sync up floors to match based on stairs
    * Look into matching through similar wall-layouts?
* Replace any hard-coded values <sup>2</sup>

**User-Interface**
* Render staircases <sup>2</sup>
* Combine floors to render entire building <sup>2</sup>
* Update upload / capture page layout & CSS <sup>1</sup>

## Future Ideas
* Add automatic stairway detection (ones represented by striped lines)
* Add automatic doorway detection (ones represented by quarter-circles)
* Find multiple possible paths
* Improve detection accuracy
    * Detect room names that are vertically-oriented
    * Detect room names that are on top of walls
* Generate specific directions based on path
* Allow users to add or remove room names
* Render elevators 
* Better creation for diagonal walls (doesn't create massive blob)
* Create mini-tutorial / tooltips