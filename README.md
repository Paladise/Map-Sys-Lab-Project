# Atlas | Changing Dimensionality of Map for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

**Image Processing**
* Improve accuracy
    * Detect text-wrapping
    * Update general room name detection (especially for 1 character ones)
* Update symbol detection 
    * Add functionality to send image of key and detect symbols with it
    * Add automatic stairway detection (ones represented by striped lines)
* Detect doorways on maps where they are not clear
* Detect resolution of map and use those values instead of hard-coded ones

**Navigation**
* Multi-floor pathfinding
    * Sync up multiple floors of map to match based on symbols
* Find multiple possible paths

**Rendering Model**
* Improve GUI / CSS
    * Update labels (i.e. door5 -> Door 5)
* Add rendering for staircases / elevators
* Add indoor-lighting