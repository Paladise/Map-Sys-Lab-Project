![Atlasan](https://i.ibb.co/y8C3GTL/pasted-image-0.png" )
## Changing Dimensionality of Maps for Indoor Navigation
*Our 2022-2023 Senior Research Lab Project.*

**People are directionally  challenged**… and so we aimed to make indoor navigation easier by allowing users to transform photos of traditional building floor maps into maneuverable models with paths that can traverse multiple levels.

### Using Atlasan

The system is broken up into the front and back-end components, where the front-end is a Django web project, and the back-end is a series of Python processing scripts (`process.py` and all the files in the `utils` folder); we specifically developed our system using TJHSST's Director hosting the front-end and JupyterHub hosting the back-end, with SSH and Ajax requests connecting the two. If anyone plans on continuing development on this project, additional measures will need to be taken to alter directories, as the current repository specifically links to my TJ JupyterHub account.

Once images are uploaded through `/upload`, the user should be redirected to `/render/<ID>`, and once all the relevant background processing is done, this is where the model can be interacted with. A complete demonstration can be found [here](https://youtu.be/gSSKYymWk1k).

### Future Ideas
* Add automatic stairway detection (ones represented by striped lines)
* Add automatic doorway detection (ones represented by quarter-circles)
* Find multiple possible paths
* Improve detection accuracy
    * Detect room names that are vertically-oriented
    * Detect room names that are on top of walls
    * Detect room names that are connected to a room with an arrow
    * Detect text wrapping better
    * Detect maps that are not black text on white background
* Generate specific directions based on path
* Allow users to add or remove room names / edit model
* Render staircases & elevators 
* Combine floors to render entire building
* Better creation for diagonal walls (don't create massive blob)
* Look into matching floors through similar wall-layouts so not only reliant on staircases
* Create mini-tutorial / tooltips on how to use app
* Be able to change speed of camera to accommodate different walking speeds
