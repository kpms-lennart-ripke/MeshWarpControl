import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import numpy as np

from views.mesh_canvas import MeshCanvas

class ImageWindow(tk.Toplevel):
    def __init__(self, title: str, width: int = 500, height: int = 600, **kwargs):
        super().__init__(**kwargs)
        self.title(title)
        
        # Set window size and position
        self.geometry(f"{width}x{height}")
        
        # Configure window to expand properly
        self.grid_rowconfigure(1, weight=1)  # Make canvas row expandable
        self.grid_columnconfigure(0, weight=1)  # Make all columns expandable
        
        # Bind resize event
        self.bind('<Configure>', self._on_window_resize)
        
        # Configure window to expand content
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Top controls frame
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Zoom controls
        zoom_frame = ttk.LabelFrame(top_frame, text="Zoom")
        zoom_frame.pack(side=tk.LEFT)
        
        ttk.Button(zoom_frame, text="-10%", command=lambda: self._on_zoom_change(-0.1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="+10%", command=lambda: self._on_zoom_change(0.1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="100%", command=self._on_zoom_reset).pack(side=tk.LEFT, padx=2)
        
        # Canvas frame that fills the window
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas that fills its container
        self.canvas = MeshCanvas(self.canvas_frame, title="")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Status bar at bottom
        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Event callbacks
        self.on_zoom_change: Optional[Callable[[float], None]] = None
        self.on_zoom_reset: Optional[Callable[[], None]] = None

    def _on_zoom_change(self, amount: float):
        """Handle zoom change"""
        self.canvas.zoom_in(amount)
        self._update_status_bar()
        if self.on_zoom_change:
            self.on_zoom_change(amount)

    def _on_zoom_reset(self):
        """Reset zoom"""
        self.canvas.reset_zoom()
        self._update_status_bar()
        if self.on_zoom_reset:
            self.on_zoom_reset()

    def _update_status_bar(self, text: Optional[str] = None):
        """Update status bar with zoom info and optional text"""
        zoom = self.canvas.get_zoom_factor()
        status = f"Zoom: {zoom*100:.0f}%"
        if text:
            status = f"{text} | {status}"
        self.status_bar.config(text=status)

    def display_image(self, image: np.ndarray):
        """Display an image on the canvas"""
        self.canvas.display_image(image)

    def update_status(self, message: str):
        """Update status bar with message"""
        self._update_status_bar(message)

    def _on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self:
            # Update canvas size to fill window
            width = event.width - 20  # Account for padding
            height = event.height - 100  # Account for controls and status bar
            self.canvas_frame.configure(width=width, height=height)
            
    def get_canvas(self) -> MeshCanvas:
        """Get the canvas widget"""
        return self.canvas
