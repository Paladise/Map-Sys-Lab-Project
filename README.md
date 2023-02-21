# Atlas | Changing Dimensionality of Map for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

**Image Processing**
* Improve accuracy
    * Detect rotated room names
    * Detect text-wrapping
    * Update general room name detection (especially for 1 character ones)
* Update symbol detection 
    * Add functionality to send image of key and detect symbols with it
    * Add automatic stairway detection (ones represented by striped lines)
* Research flood-fill alternatives that are faster for determining bounding boxes
* Detect doorways on maps where doors are not clear
* Detect size / resolution of map and use those values instead of hard-coded ones

**Navigation**
* Multi-floor pathfinding
    * Sync up multiple floors of map to match based on symbols
* Find multiple possible paths

**Rendering Model**
* Improve GUI / CSS
    * Should be mobile friendly
    * Update labels (i.e. door5 -> Door 5)
* Add rendering for staircases / elevators
* Add lighting

**Miscellaneous**
* Add option to copy link for certain map