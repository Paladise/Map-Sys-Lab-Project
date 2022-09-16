import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()

image = Image.open("detected_lines.png")
pix = image.load()

# Create an object of tkinter ImageTk
tk_image = ImageTk.PhotoImage(image)

label = tk.Label(root, image = tk_image)
label.pack()
root.update()

q = [(x, y) for x in range(image.width) for y in range(image.height)]
count = 0

while q:
    x, y = q.pop()

    r, g, b = pix[x, y]
    if r + g + abs(b - 255) < 220: # If blueish pixel
        pix[x, y] = (0, 0, 255) # Make pixel actual blue
        count += 1
        if count == 1000:
            count = 0
            # Create an object of tkinter ImageTk
            tk_image = ImageTk.PhotoImage(image)
            label.configure(image = tk_image)
            label.pack()
            root.update()
        
        go_through = (-3, -2, -1, 1, 2, 3)

        # Loop through neighboring pixels 
        for x1 in go_through:
            for y1 in go_through:
                try:
                    r, g, b = pix[x + x1, y + y1]
                except:
                    continue
                if abs(r - 255) + abs(g - 255) + abs(b - 255) < 300: # If whiteish pixel
                    pix[x + x1, y + y1] = (0, 0, 255) # Make pixel blue
                    q.append((x + x1, y + y1)) # Add to q


# Remove extra whiteish pixels

for x in range(image.width):
    for y in range(image.height):
        
        if pix[x, y] != (0, 0, 255):
            pix[x, y] = (0, 0, 0)
        else:
            pix[x, y] = (0, 0, 255)
        
image.show()
image.save("only_walls.png")

root.mainloop()
        