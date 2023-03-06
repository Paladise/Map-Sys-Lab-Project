# Atlas | Changing Dimensionality of Map for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

**Image Processing**
* Update symbol detection 
    * Add functionality to send image(s) of key and detect symbols with it
    * Add automatic stairway detection (ones represented by striped lines)
* Detect doorways on maps where they are not clear
* Improve accuracy
    * Detect text-wrapping
    * Enhance text detection (especially for 1-character rooms)
* Update labels (i.e. door5 -> Door 5)

**Navigation**
* Multi-floor pathfinding
    * Sync up multiple floors of map to match based on stairs
* Replace hard-coded values
* Find multiple possible paths

**Rendering Model**
* Render staircases & elevators
* Add indoor-lighting
* Improve UI