# Atlas | Changing Dimensionality of Map for Indoor Navigation

2022-2023 Senior Research Lab Project

## Features In Progress

**Image Processing**
* Add ability to flatten / crop images before processing to improve accuracy
* Detect rotated room names
* Detect text-wrapping
* Improve room name detection (especially for single character room names)
* Update symbol detection 
    * Add functionality to send image of key for backend processing
    * Research image similarity measures and viable thresholds for similarity
    * Update what the labels are for the symbols, i.e. door5 -> Door 5
    * Add automatic stairway detection (ones represented by striped lines)
* Research flood-fill alternatives that are faster for determining bounding boxes
* Detect contour of building
* Detect arrows pointing to room names
* Detect size / resolution of map and use those values instead of hard-coded ones

**Navigation**
* Sync up multiple floors of map to match based on symbols
    * Possibly resize maps as well so that they match up in size for birds-eye view
* Update pathfinding
    * Search for certain number of stairways / elevators then teleport to next floor
    * Multiple paths
    * Add option to only use elevators for accessibility needs

**Rendering Model**
* Improve GUI / CSS
    * Should be mobile friendly
* Add actual rendering for floors / staircases / elevators
* Add lighting to make more realistic