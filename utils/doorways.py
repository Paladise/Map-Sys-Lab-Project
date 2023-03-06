"""
Save boxes of identified rooms (remove ones that bound nothing)

For every room name

    Expand out in all 4 cardinal directions until hits a wall

        - Use to add padding for every room, but also use it as 
        rudimentary way of getting doorways
    
For every room name
    For every direction

        Search in same direction along wall until comes along blank pixel and continue expanding
        (stop if it hits another wall)

        Check if made line intersects any (expanded) room boxes

        If it doesn't intersect, assume it's a hallway
        
            Create doorway by removing pixels that are walls
"""