import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Tuple
import numpy as np
import cv2
from models.mesh_grid import MeshPoint
from utils.image_utils import display_image

class MeshCanvas(ttk.Frame):
    def __init__(self, master, title: str, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create title label
        title_label = ttk.Label(self, text=title)
        title_label.pack(pady=5)
        
        # Get parent window size for calculating frame size
        self.update_idletasks()  # Ensure geometry is updated
        window_width = self.winfo_toplevel().winfo_width()
        frame_width = (window_width - 40) // 2  # Account for padding
        
        # Create frame that fills parent
        self.outer_frame = ttk.Frame(self)
        self.outer_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Create canvas frame with proper expansion
        self.canvas_frame = ttk.Frame(self.outer_frame)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)
        
        # Configure frame to expand properly
        self.outer_frame.grid_rowconfigure(0, weight=1)
        self.outer_frame.grid_columnconfigure(0, weight=1)
        
        # Configure canvas frame for expansion
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas with scrollable region
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', width=400, height=400)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Bind resize event
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Add scrollbars
        self.y_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.x_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)
        
        # Zoom settings
        self.zoom_factor = 1.0
        self.original_image = None
        self.zoomed_image = None
        
        # Image reference
        self.photo = None
        
        # Mesh drawing settings
        self.line_color = "blue"
        self.point_color = "red"
        self.text_color = "black"
        self.point_radius = 3
        self.text_offset = -10
        self.font = ("Arial", 8)
        
        # Mouse tracking
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.on_mouse_move: Optional[Callable[[float, float], None]] = None

    def display_image(self, image: np.ndarray):
        """Display an image on the canvas"""
        self.original_image = image.copy()
        self._update_zoomed_image()

    def _on_canvas_configure(self, event):
        """Handle canvas resize events"""
        if self.original_image is not None:
            self._update_zoomed_image()

    def _update_zoomed_image(self):
        """Update the displayed image based on zoom factor"""
        if self.original_image is None:
            return
            
        h, w = self.original_image.shape[:2]
        new_w = int(w * self.zoom_factor)
        new_h = int(h * self.zoom_factor)
        
        # Resize image
        self.zoomed_image = cv2.resize(self.original_image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Update scrollregion to match image size
        self.canvas.config(scrollregion=(0, 0, new_w, new_h))
        
        # Display image
        self.photo = display_image(self.zoomed_image, self.canvas)
        # Redraw mesh with new zoom if we have points
        if hasattr(self, 'current_points'):
            self.clear_mesh()
            self.draw_mesh_lines(self.current_points)
            self.draw_mesh_points(self.current_points)

    def set_zoom(self, factor: float):
        """Set zoom factor and update display"""
        self.zoom_factor = max(0.1, min(5.0, factor))  # Limit zoom range
        self._update_zoomed_image()

    def zoom_in(self, amount: float = 0.1):
        """Increase zoom by specified amount"""
        self.set_zoom(self.zoom_factor + amount)

    def zoom_out(self, amount: float = 0.1):
        """Decrease zoom by specified amount"""
        self.set_zoom(self.zoom_factor - amount)

    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.set_zoom(1.0)

    def get_zoom_factor(self) -> float:
        """Get current zoom factor"""
        return self.zoom_factor

    def _on_mouse_move(self, event):
        """Handle mouse movement and update coordinates"""
        if self.on_mouse_move:
            # Convert coordinates to original image space with subpixel precision
            x = event.x / self.zoom_factor
            y = event.y / self.zoom_factor
            self.on_mouse_move(x, y)

    def clear_mesh(self):
        """Clear all mesh elements from the canvas"""
        self.canvas.delete("mesh")

    def draw_mesh_lines(self, points: list[list[MeshPoint]]):
        """Draw mesh grid lines"""
        if not points:
            return
        # Store current points for redrawing during zoom
        self.current_points = points
            
        rows = len(points)
        cols = len(points[0])
        
        # Draw horizontal lines
        for r in range(rows):
            for c in range(cols - 1):
                p1 = points[r][c]
                p2 = points[r][c + 1]
                self.canvas.create_line(
                    p1.x * self.zoom_factor, p1.y * self.zoom_factor,
                    p2.x * self.zoom_factor, p2.y * self.zoom_factor,
                    fill=self.line_color,
                    tags="mesh"
                )

        # Draw vertical lines
        for c in range(cols):
            for r in range(rows - 1):
                p1 = points[r][c]
                p2 = points[r + 1][c]
                self.canvas.create_line(
                    p1.x * self.zoom_factor, p1.y * self.zoom_factor,
                    p2.x * self.zoom_factor, p2.y * self.zoom_factor,
                    fill=self.line_color,
                    tags="mesh"
                )

    def draw_mesh_points(self, points: list[list[MeshPoint]], show_coordinates: bool = True):
        """Draw mesh points and optionally their coordinates"""
        if not points:
            return
            
        for row in points:
            for point in row:
                # Scale coordinates
                x = point.x * self.zoom_factor
                y = point.y * self.zoom_factor
                
                # Draw point
                self.canvas.create_oval(
                    x - self.point_radius, y - self.point_radius,
                    x + self.point_radius, y + self.point_radius,
                    fill=self.point_color,
                    tags="mesh"
                )
                
                # Draw coordinates
                if show_coordinates:
                    self.canvas.create_text(
                        x, y + self.text_offset,
                        text=f"({point.row},{point.col})",
                        font=self.font,
                        fill=self.text_color,
                        tags="mesh"
                    )

    def bind_click(self, callback: Callable[[float, float], None]):
        """Bind left mouse click event with subpixel precision"""
        self.canvas.bind("<Button-1>", lambda e: callback(e.x/self.zoom_factor, e.y/self.zoom_factor))

    def bind_drag(self, callback: Callable[[float, float], None]):
        """Bind mouse drag event with subpixel precision"""
        self.canvas.bind("<B1-Motion>", lambda e: callback(e.x/self.zoom_factor, e.y/self.zoom_factor))

    def bind_release(self, callback: Callable[[], None]):
        """Bind mouse release event"""
        self.canvas.bind("<ButtonRelease-1>", lambda e: callback())

    def get_size(self) -> Tuple[int, int]:
        """Get current canvas size"""
        return self.canvas.winfo_width(), self.canvas.winfo_height()
