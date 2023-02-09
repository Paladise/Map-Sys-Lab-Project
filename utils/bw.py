def convert_to_bw(image, threshold):
    """
    Converts a PIL image to only black and white pixels
    given a black and white threshold
    """

    width, height = image.size[0], image.size[1]
    pixels = image.load()

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            if 0.2126*r + 0.7152*g + 0.0722*b < threshold: # Check if pixel is relatively dark
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)

    return image