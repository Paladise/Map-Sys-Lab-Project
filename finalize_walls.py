import tkinter
from PIL import Image, ImageTk
from tkinter import *
from PIL import ImageTk, Image

root = tkinter.Tk()

img = Image.open("detected_lines.jpg")
pix = img.load()

# Create an object of tkinter ImageTk
tk_img = ImageTk.PhotoImage(img)

label = Label(root, image = tk_img)
label.pack()
root.update()

q = [(x, y) for x in range(img.width) for y in range(img.height)]
count = 0

while q:
    x, y = q.pop()

    r, g, b = pix[x, y]
    if r + g + abs(b - 255) < 220: # If blueish pixel
        pix[x, y] = (0, 0, 255) # Make pixel actual blue
        count += 1
        if count == 1000:
            print("updated")
            count = 0
            # Create an object of tkinter ImageTk
            img.save("temp.jpg")
            tk_img = ImageTk.PhotoImage(Image.open("temp.jpg"))
            label.configure(image = tk_img)
            label.pack()
            root.update()

        # Loop through neighboring pixels 
        for x1 in (-2, -1, 1, 2):
            for y1 in (-2, -1, 1, 2):
                try:
                    r, g, b = pix[x + x1, y + y1]
                except:
                    continue
                if abs(r - 255) + abs(g - 255) + abs(b - 255) < 220: # If whiteish pixel
                    pix[x + x1, y + y1] = (0, 0, 255) # Make pixel blue
                    q.append((x + x1, y + y1)) # Add to q


# Remove extra whiteish pixels

for x in range(img.width):
    for y in range(img.height):
        
        if pix[x, y] != (0, 0, 255):
            pix[x, y] = (0, 0, 0)
        else:
            pix[x, y] = (0, 0, 255)
        

img.show()
img.save("only_walls_finalized.jpg")

new_img = Image.open("only_walls_finalized.jpg")
new_img = new_img.convert("RGB")
new_pix = new_img.load()

for x in range(new_img.width):
    for y in range(new_img.height):
        r, g, b = new_pix[x, y]      
        if r + g + abs(b - 255) < 100:
            new_pix[x, y] = (255, 0, 0)
        else:
            new_pix[x, y] = (0, 0, 0)

new_img.save("FINALIZED.jpg")
print("Finished")

root.mainloop()
        