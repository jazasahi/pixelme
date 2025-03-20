import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO

def resize_image(image, max_width=1080, max_height=2400):
    """Resizes an image while maintaining aspect ratio to fit within wallpaper dimensions."""
    width, height = image.size
    aspect_ratio = width / height

    if width > max_width:
        width = max_width
        height = int(width / aspect_ratio)
    if height > max_height:
        height = max_height
        width = int(height * aspect_ratio)

    return image.resize((width, height))

def pixelate_image(image, pixel_size, shape='square'):
    """Pixelates an image with a chosen shape."""
    width, height = image.size
    image = image.convert("RGB")
    pixels = image.load()

    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            r_sum, g_sum, b_sum, count = 0, 0, 0, 0
            for py in range(y, min(y + pixel_size, height)):
                for px in range(x, min(x + pixel_size, width)):
                    r, g, b = pixels[px, py]
                    r_sum += r
                    g_sum += g
                    b_sum += b
                    count += 1

            if count > 0:
                avg_r = r_sum // count
                avg_g = g_sum // count
                avg_b = b_sum // count
                avg_color = (avg_r, avg_g, avg_b)

                draw = ImageDraw.Draw(image)
                if shape == 'square':
                    draw.rectangle([(x, y), (min(x + pixel_size, width), min(y + pixel_size, height))], fill=avg_color)
                elif shape == 'circle':
                    center_x = x + pixel_size // 2
                    center_y = y + pixel_size // 2
                    draw.ellipse([(x, y), (min(x + pixel_size, width), min(y + pixel_size, height))], fill=avg_color)
                elif shape == 'star':
                    points = []
                    center_x = x + pixel_size // 2
                    center_y = y + pixel_size // 2
                    outer_radius = pixel_size // 2
                    inner_radius = outer_radius // 2
                    for i in range(5):
                        angle = np.pi / 2 + i * 2 * np.pi / 5
                        outer_x = center_x + outer_radius * np.cos(angle)
                        outer_y = center_y + outer_radius * np.sin(angle)
                        points.append((outer_x, outer_y))
                        angle += np.pi / 5
                        inner_x = center_x + inner_radius * np.cos(angle)
                        inner_y = center_y + inner_radius * np.sin(angle)
                        points.append((inner_x, inner_y))
                    draw.polygon(points, fill=avg_color)

    return image

def download_image(img):
    """Converts PIL image to bytes for download."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

st.title("Image Pixel Art Generator")

uploaded_file = st.file_uploader("Upload an image (optimized for smartphone wallpaper)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_column_width=True)

        resized_image = resize_image(image)
        st.info("Image resized to standard smartphone wallpaper dimensions.")

        pixel_size = st.slider("Pixel Size", 5, 50, 20, help="Adjust to control the level of pixelation.")
        pixel_shape = st.radio("Pixel Shape", ['square', 'circle', 'star'], index=0, help="Choose the shape of the pixels.")

        pixelated_image = pixelate_image(resized_image, pixel_size, shape=pixel_shape)
        st.image(pixelated_image, caption="Pixelated Image", use_column_width=True)

        st.success("Your pixel art is ready!")

        download_button = st.download_button(
            label="Download Pixel Art",
            data=download_image(pixelated_image),
            file_name="pixel_art.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")