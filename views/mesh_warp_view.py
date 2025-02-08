import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Callable, Optional
import numpy as np

from views.mesh_canvas import MeshCanvas
from viewmodels.mesh_warp_vm import MeshWarpViewModel
from models.mesh_grid import MeshPoint

class MeshWarpView(ttk.Frame):
    def __init__(self, master, viewmodel: MeshWarpViewModel, **kwargs):
        super().__init__(master, **kwargs)
        self.vm = viewmodel
        
        # Set up view model callbacks
        self.vm.on_input_image_changed = self._on_input_image_changed
        self.vm.on_output_image_changed = self._on_output_image_changed
        self.vm.on_mesh_updated = self._on_mesh_updated
        self.vm.on_status_changed = self._on_status_changed
        
        self.create_widgets()
        
        # Load default image if available
        default_image = os.path.join("images", "Test Image1-051503.bmp")
        if os.path.exists(default_image):
            self.vm.load_image(default_image)

    def create_widgets(self):
        # Top controls
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        load_button = ttk.Button(top_frame, text="Load Image", command=self._on_load_click)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        zoom_frame = ttk.LabelFrame(top_frame, text="Zoom")
        zoom_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(zoom_frame, text="-10%", command=lambda: self._on_zoom_change(-0.1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="+10%", command=lambda: self._on_zoom_change(0.1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="100%", command=self._on_zoom_reset).pack(side=tk.LEFT, padx=2)
        
        # Canvas area with fixed size
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(padx=5, pady=5)
        
        # Left frame for input canvas
        left_frame = ttk.Frame(canvas_frame)
        left_frame.pack(side=tk.LEFT, padx=5)
        
        # Input canvas
        self.input_canvas = MeshCanvas(left_frame, title="Input Image")
        self.input_canvas.pack()
        
        # Bind canvas events
        self.input_canvas.bind_click(self._on_canvas_click)
        self.input_canvas.bind_drag(self._on_canvas_drag)
        self.input_canvas.bind_release(self._on_canvas_release)
        self.input_canvas.on_mouse_move = self._on_input_mouse_move
        
        # Right frame for output canvas
        right_frame = ttk.Frame(canvas_frame)
        right_frame.pack(side=tk.LEFT, padx=5)
        
        # Output canvas
        self.output_canvas = MeshCanvas(right_frame, title="Output Image")
        self.output_canvas.pack()
        self.output_canvas.on_mouse_move = self._on_output_mouse_move
        
        # Controls area
        controls_frame = ttk.LabelFrame(self, text="Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid controls
        grid_frame = ttk.Frame(controls_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(grid_frame, text="Rows:").pack(side=tk.LEFT, padx=5)
        self.rows_var = tk.StringVar(value="5")
        rows_entry = ttk.Entry(grid_frame, textvariable=self.rows_var, width=5)
        rows_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(grid_frame, text="Cols:").pack(side=tk.LEFT, padx=5)
        self.cols_var = tk.StringVar(value="5")
        cols_entry = ttk.Entry(grid_frame, textvariable=self.cols_var, width=5)
        cols_entry.pack(side=tk.LEFT, padx=5)
        
        resize_button = ttk.Button(grid_frame, text="Resize Grid", command=self._on_resize_click)
        resize_button.pack(side=tk.LEFT, padx=20)
        
        # Output size controls
        size_frame = ttk.Frame(controls_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(size_frame, text="Output Width:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.StringVar(value="400")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=5)
        width_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(size_frame, text="Output Height:").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.StringVar(value="400")
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=5)
        height_entry.pack(side=tk.LEFT, padx=5)
        
        update_button = ttk.Button(size_frame, text="Update", command=self._on_update_click)
        update_button.pack(side=tk.LEFT, padx=20)
        
        # Save/Load controls
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Save Mesh", command=self._on_save_mesh_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Mesh", command=self._on_load_mesh_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Result", command=self._on_save_result_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Maps", command=self._on_save_maps_click).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, padx=5, pady=5)

    def _on_zoom_change(self, amount: float):
        """Handle zoom change for both canvases"""
        self.input_canvas.zoom_in(amount)
        self.output_canvas.zoom_in(amount)
        self._update_status_bar()

    def _on_zoom_reset(self):
        """Reset zoom for both canvases"""
        self.input_canvas.reset_zoom()
        self.output_canvas.reset_zoom()
        self._update_status_bar()

    def _update_status_bar(self, text: Optional[str] = None):
        """Update status bar with zoom info and optional text"""
        zoom = self.input_canvas.get_zoom_factor()
        status = f"Zoom: {zoom*100:.0f}%"
        if text:
            status = f"{text} | {status}"
        self.status_bar.config(text=status)

    def _on_input_mouse_move(self, x: int, y: int):
        """Handle mouse movement over input canvas"""
        point_info = self.vm.get_point_info(x, y)
        if point_info:
            point, _ = point_info
            self._update_status_bar(f"Input: ({x:.1f}, {y:.1f}) | Grid: (row={point.row}, col={point.col})")
        else:
            self._update_status_bar(f"Input: ({x:.1f}, {y:.1f})")

    def _on_output_mouse_move(self, x: int, y: int):
        """Handle mouse movement over output canvas"""
        self._update_status_bar(f"Output: ({x:.1f}, {y:.1f})")

    def _on_load_click(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filepath:
            self.vm.load_image(filepath)

    def _on_resize_click(self):
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            self.vm.resize_grid(rows, cols)
        except ValueError:
            self._on_status_changed("Invalid grid dimensions")

    def _on_update_click(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            self.vm.update_output_image(width, height)
        except ValueError:
            self._on_status_changed("Invalid output dimensions")

    def _on_save_mesh_click(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            self.vm.save_mesh(filepath)

    def _on_load_mesh_click(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            self.vm.load_mesh(filepath)

    def _on_save_result_click(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.vm.save_result(filepath)

    def _on_save_maps_click(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".npz",
            filetypes=[("NumPy files", "*.npz")]
        )
        if filepath:
            self.vm.save_maps(filepath)

    def _on_canvas_click(self, x: int, y: int):
        point_info = self.vm.get_point_info(x, y)
        if point_info:
            point, _ = point_info
            self.vm.move_point(point.row, point.col, x, y)

    def _on_canvas_drag(self, x: int, y: int):
        point_info = self.vm.get_point_info(x, y)
        if point_info:
            point, _ = point_info
            self.vm.move_point(point.row, point.col, x, y)
            self._update_status_bar(f"Moving point ({point.row}, {point.col}) to ({x:.1f}, {y:.1f})")

    def _on_canvas_release(self):
        self.vm.update_output_image()

    def _on_input_image_changed(self, image: np.ndarray):
        self.input_canvas.display_image(image)

    def _on_output_image_changed(self, image: np.ndarray):
        self.output_canvas.display_image(image)

    def _on_mesh_updated(self):
        if self.vm.mesh_grid:
            self.input_canvas.clear_mesh()
            self.input_canvas.draw_mesh_lines(self.vm.mesh_grid.points)
            self.input_canvas.draw_mesh_points(self.vm.mesh_grid.points)

    def _on_status_changed(self, message: str):
        self._update_status_bar(message)
