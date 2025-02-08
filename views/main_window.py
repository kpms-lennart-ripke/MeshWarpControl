import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Optional
import numpy as np

from views.image_window import ImageWindow
from viewmodels.mesh_warp_vm import MeshWarpViewModel

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Mesh Warp Control")
        self.geometry("400x300")
        
        # Create view model
        self.vm = MeshWarpViewModel()
        
        # Create image windows with larger size
        self.input_window = ImageWindow(title="Input Image", width=800, height=800)
        self.result_window = ImageWindow(title="Result Image", width=800, height=800)
        
        # Position windows with more space
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Main window in center bottom
        x = (screen_width - 400) // 2
        y = screen_height - 400  # Position at bottom
        self.geometry(f"+{x}+{y}")
        
        # Input window on left
        input_x = (screen_width // 2 - 800) // 2  # Center in left half
        input_y = (screen_height - 800) // 2  # Center vertically
        self.input_window.geometry(f"+{input_x}+{input_y}")
        
        # Result window on right
        result_x = screen_width // 2 + (screen_width // 2 - 800) // 2  # Center in right half
        self.result_window.geometry(f"+{result_x}+{input_y}")
        
        # Set up callbacks
        self.vm.on_input_image_changed = self._on_input_image_changed
        self.vm.on_output_image_changed = self._on_output_image_changed
        self.vm.on_mesh_updated = self._on_mesh_updated
        self.vm.on_status_changed = self._on_status_changed
        
        # Set up canvas callbacks
        input_canvas = self.input_window.get_canvas()
        input_canvas.bind_click(self._on_canvas_click)
        input_canvas.bind_drag(self._on_canvas_drag)
        input_canvas.bind_release(self._on_canvas_release)
        input_canvas.on_mouse_move = self._on_input_mouse_move
        
        result_canvas = self.result_window.get_canvas()
        result_canvas.on_mouse_move = self._on_output_mouse_move
        
        self.create_widgets()
        
        # Load default image if available
        default_image = os.path.join("images", "Test Image1-051503.bmp")
        if os.path.exists(default_image):
            self.vm.load_image(default_image)

    def create_widgets(self):
        # Main controls
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Image controls
        image_frame = ttk.LabelFrame(main_frame, text="Image")
        image_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(image_frame, text="Load Image", command=self._on_load_click).pack(padx=5, pady=5)
        
        # Grid controls
        grid_frame = ttk.LabelFrame(main_frame, text="Grid")
        grid_frame.pack(fill=tk.X, pady=5)
        
        # Row/Col controls
        rc_frame = ttk.Frame(grid_frame)
        rc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(rc_frame, text="Rows:").pack(side=tk.LEFT)
        self.rows_var = tk.StringVar(value="5")
        ttk.Entry(rc_frame, textvariable=self.rows_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(rc_frame, text="Cols:").pack(side=tk.LEFT, padx=5)
        self.cols_var = tk.StringVar(value="5")
        ttk.Entry(rc_frame, textvariable=self.cols_var, width=5).pack(side=tk.LEFT)
        
        ttk.Button(grid_frame, text="Resize Grid", command=self._on_resize_click).pack(padx=5, pady=5)
        
        # Output size controls
        size_frame = ttk.LabelFrame(main_frame, text="Output Size")
        size_frame.pack(fill=tk.X, pady=5)
        
        # Width/Height controls
        wh_frame = ttk.Frame(size_frame)
        wh_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(wh_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="400")
        ttk.Entry(wh_frame, textvariable=self.width_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(wh_frame, text="Height:").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.StringVar(value="400")
        ttk.Entry(wh_frame, textvariable=self.height_var, width=5).pack(side=tk.LEFT)
        
        ttk.Button(size_frame, text="Update", command=self._on_update_click).pack(padx=5, pady=5)
        
        # Save/Load controls
        save_frame = ttk.LabelFrame(main_frame, text="Save/Load")
        save_frame.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(save_frame)
        button_frame.pack(padx=5, pady=5)
        
        ttk.Button(button_frame, text="Save Mesh", command=self._on_save_mesh_click).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load Mesh", command=self._on_load_mesh_click).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save Result", command=self._on_save_result_click).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save Maps", command=self._on_save_maps_click).pack(side=tk.LEFT, padx=2)

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

    def _on_canvas_click(self, x: float, y: float):
        point_info = self.vm.get_point_info(x, y)
        if point_info:
            point, _ = point_info
            self.vm.move_point(point.row, point.col, x, y)

    def _on_canvas_drag(self, x: float, y: float):
        point_info = self.vm.get_point_info(x, y)
        if point_info:
            point, _ = point_info
            self.vm.move_point(point.row, point.col, x, y)
            self.input_window.update_status(f"Moving point ({point.row}, {point.col}) to ({x:.1f}, {y:.1f})")

    def _on_canvas_release(self):
        self.vm.update_output_image()

    def _on_input_mouse_move(self, x: float, y: float):
        point_info = self.vm.get_point_info(x, y)
        if point_info:
            point, _ = point_info
            self.input_window.update_status(f"Input: ({x:.1f}, {y:.1f}) | Grid: (row={point.row}, col={point.col})")
        else:
            self.input_window.update_status(f"Input: ({x:.1f}, {y:.1f})")

    def _on_output_mouse_move(self, x: float, y: float):
        self.result_window.update_status(f"Output: ({x:.1f}, {y:.1f})")

    def _on_input_image_changed(self, image: np.ndarray):
        self.input_window.display_image(image)

    def _on_output_image_changed(self, image: np.ndarray):
        self.result_window.display_image(image)

    def _on_mesh_updated(self):
        if self.vm.mesh_grid:
            canvas = self.input_window.get_canvas()
            canvas.clear_mesh()
            canvas.draw_mesh_lines(self.vm.mesh_grid.points)
            canvas.draw_mesh_points(self.vm.mesh_grid.points)

    def _on_status_changed(self, message: str):
        self.input_window.update_status(message)
