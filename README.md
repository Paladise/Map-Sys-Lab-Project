# Atlasan | Changing Dimensionality of Maps for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

Fix bugs :D

**Navigation**
* Multi-floor pathfinding
    * Sync up floors to match based on stairs
* Replace any hard-coded values 

**User-Interface**
* Combine floors to render entire building

## Future Ideas
* Add automatic stairway detection (ones represented by striped lines)
* Add automatic doorway detection (ones represented by quarter-circles)
* Find multiple possible paths
* Improve detection accuracy
    * Detect room names that are vertically-oriented
    * Detect room names that are on top of walls
    * Detect room names that are connected to a room with an arrow
    * Detect text wrapping better
* Generate specific directions based on path
* Allow users to add or remove room names / edit model
* Render staircases & elevators 
* Better creation for diagonal walls (doesn't create massive blob)
* Look into matching floors through similar wall-layouts so not only reliant on staircases
* Create mini-tutorial / tooltips
* Enable detection on maps that are not black text on white background