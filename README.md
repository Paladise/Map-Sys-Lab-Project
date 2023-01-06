# Atlas
## Changing Dimensionality of Map for Indoor Navigation

Our 2022-2023 Senior Research Lab Project

## To-do List

* Flatten / crop images before processing to improve accuracy
* Detect rotated room names & detect text-wrapping
* Improve room name detection (especially for single character room names)
* Update symbol detection 
    * Add functionality to send image of key for backend processing
    * Research image similarity measures and viable thresholds for similarity
    * Update what the labels are for the symbols, i.e. door5 -> Door 5
* Sync up multiple floors of map to match based on symbols
    * Possibly resize maps as well so that they match up in size for birds-eye view
* Update pathfinding
    * Search for certain number of stairways / elevators then teleport to next floor
    * Add option to only use elevators for accessibility needs
    * Make sure path doesn't go through other rooms (rooms that are solely numbers should be flood filled around them and treated as walls)
* Research faster algorithms than flood-filling for determining boxes and implement them
* Improve GUI and CSS styling (should be mobile compatible)
* Add actual rendering for floors / staircases / elevators
    * Improve lighting to make more realistic
* Detect arrows pointing to room names
    * Detect contour of building
* Detect rooms that are not directly connected to hallway (lacking doorways)
* Match up floors that do not have stairways visibly labeled, ex: https://www2.montgomeryschoolsmd.org/schools/northwoodhs/about/map