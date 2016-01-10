# pygame-tile-editor

## IMAGES:
background.png & navigator.png are used for UI
reds.png, blues.png & greens.png are placeholder tilesets until the ability to load tilesets is added

## CODE:
buttonlib.py is currently unused by the main project (map_view.py), it was created as a more general-use library using code I created for map_view.py. 
Eventually I will get around to making map_view use buttonlib (which should clean map_view up a bit as well)

map_view.py is (unfortunatly) where all of the code is located. As stated above it will be cleaned up soon. This is the file to run.

## USAGE:
3 main points of interest:
  - the main view on the right hand side, where you see and edit the map. 
  - the tile-selecter on the lower left hand side, where you select first a tileset (left-column) then a specific tile (right-column) from this tileset
  - the buttons and stuff in the upper left hand side. 
  
## Main view:
scroll wheel to zoom in and out, WASD or arrow-keys to move around, Q to save, E to load, R for new file.
right click and drag to move around to map or hold down middle mouse button to scroll around the map.
left click to "paint".

## Tile-selecter:
scroll wheel to scroll up and down
left click to select a tiletype and tileid.

## Buttons:
   -on the upper-right hand side there are 8 buttons (the top 4 are the only ones currently in use). These are paint, fill, select and erase.
   -just above the tile selecter is the layer-selecter. This is the layer you are currently drawing on. The map will by default show this layer and everything below it. The eye to the right of the text-box toggles single-layer-view, if the eye is outlined in red the map is only drawing the selected layer. The arrows either side of the layer selection move the layer up or down one.
   -The text-box should be fairly obvious, give it focus and type to enter text, use left/right arrows to move the cursor left/right and use
backspace to get rid of text. You cannot click to place the cursor (sorry).
   -To the right of the text-box, in order from left to right, are the save, load and new-file buttons. Which should be obvious as to their function.
  
There are tooltips on most of these.

Please feel free to offer any suggestions/criticisms. 

##Things todo:
   -Add the ability to load tilesets
   -add the ability to set the width/height of new maps
   -add the ability to set the width/height of current maps
