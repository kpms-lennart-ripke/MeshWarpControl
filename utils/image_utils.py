import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from typing import Tuple

def load_grayscale_image(filepath: str) -> np.ndarray:
    """Load an image in grayscale format"""
    image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise Exception(f"Failed to load image from {filepath}")
    return image

def create_tk_image(image: np.ndarray) -> ImageTk.PhotoImage:
    """Convert OpenCV image to Tkinter PhotoImage"""
    # Convert OpenCV grayscale image to PIL format
    image_pil = Image.fromarray(image).convert('L')
    # Convert PIL image to PhotoImage
    return ImageTk.PhotoImage(image=image_pil)

def display_image(image: np.ndarray, canvas: tk.Canvas) -> ImageTk.PhotoImage:
    """Display an image on a canvas and return the PhotoImage"""
    h, w = image.shape[:2]
    photo = create_tk_image(image)
    
    # Clear previous image
    canvas.delete("image")
    
    # Create image centered in canvas
    canvas.create_image(w//2, h//2, anchor=tk.CENTER, image=photo, tags="image")
    
    return photo  # Return to prevent garbage collection

def get_canvas_size(canvas: tk.Canvas) -> Tuple[int, int]:
    """Get the current size of a canvas"""
    return canvas.winfo_width(), canvas.winfo_height()
