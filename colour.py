import numpy as np
import pandas as pd
from PIL import Image
from sklearn.cluster import KMeans
import math
import fast_colorthief

theme_colors = np.array([
        [107, 104, 232],    # Sky Blue
        [241, 146, 114],    # Apricot
        [241, 202, 114],    # Yellow
        [107, 123, 211],    # Slate blue-y
        [224, 110, 154],    # Pink
        # [247, 247, 247],    # Off-White
        [155, 111, 223],    # Purple
        [217, 106, 107],    # Red 
        [116, 204, 36],      # Apple Green
    ])

def euclidean_distance(color1, color2):
    # Calculate the Euclidean distance between two RGB colors
    return np.sqrt(np.sum((color1 - color2)**2))


import colorsys

def is_bright_color(rgb_color, threshold=0.3):
    # Convert RGB color to HSL color space
    hsl_color = colorsys.rgb_to_hls(*[x / 255.0 for x in rgb_color])

    # Extract lightness (L) value from HSL color
    lightness = hsl_color[1]

    # Check if the lightness value is above the threshold
    return lightness >= threshold

import random
def get_random():
    return random.randint(1,6) % 2

def is_close_to_white(rgb_color, threshold=50):
    # Calculate the Euclidean distance between the color and white
    distance = math.sqrt(sum((c - 255) ** 2 for c in rgb_color))

    # Check if the distance is less than the threshold
    return distance < threshold

def brighten_color(rgb_color, brightness_factor):
    # Ensure brightness_factor is in the range [0, 1]
    brightness_factor = max(0, min(1, brightness_factor))

    # Brighten the color by scaling each color component
    r, g, b = rgb_color
    brightened_r = min(255, int(r + (1 - r / 255) * brightness_factor * 255))
    brightened_g = min(255, int(g + (1 - g / 255) * brightness_factor * 255))
    brightened_b = min(255, int(b + (1 - b / 255) * brightness_factor * 255))

    return (brightened_r, brightened_g, brightened_b)

def find_closest_color(img):
    

    transparent_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    og_img = img.convert("RGB")
    img = img.convert("RGBA")
    # Iterate over the pixels in the original image
    for x in range(img.width):
        for y in range(img.height):
            # Get the RGBA value of the pixel
            pixel = og_img.getpixel((x, y))
            if not is_close_to_white(pixel):

            # Check if the pixel is not white
            # if r + g + b < 720:
                # Paste the pixel onto the transparent image
                transparent_img.putpixel((x, y), (pixel[0], pixel[1], pixel[2], 255))
    
    img = transparent_img

    colors = fast_colorthief.get_dominant_color(np.array(img.convert("RGBA")), quality=1)
    
    
    target_color = colors
    while not is_bright_color(target_color):
        target_color = brighten_color(target_color, 0.01)
    # return target_color
    # for color in colors:
    #     if is_bright_color(color):
    #         # if get_random():
    #         target_color = color
    #         break
    
    # return target_color

    closest_color = None
    min_distance = float('inf')

    for color in theme_colors:
        distance = euclidean_distance(target_color, color)
        if distance < min_distance:
            closest_color = color
            min_distance = distance

    return closest_color

if __name__ == "__main__":
    # Image path
    image_path = "path/to/your/image.jpg"

    # Theme colors (you can add more colors or change as needed)
    

    # Get the most dominant color
    dominant_color = get_dominant_color(image_path, theme_colors)

    print("Most Dominant Color:", dominant_color)
