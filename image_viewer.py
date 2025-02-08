import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
import numpy as np
import json
from PIL import Image, ImageTk
import os

class MeshWarpApp:
    def __init__(self, master):
        self.master = master
        master.title("Mesh Warp Transformation")

        self.input_image = None
        self.output_image = None
        self.mesh_grid = None
        self.mapX = None
        self.mapY = None
        self.mesh_points = []

        self.create_widgets()
        
        # Load default image
        default_image = os.path.join("images", "Test Image1-051503.bmp")
        if os.path.exists(default_image):
            self.load_image(default_image)

    def create_widgets(self):
        # Load Image Button
        load_button = ttk.Button(self.master, text="Load Image", command=lambda: self.load_image())
        load_button.grid(row=0, column=0, padx=5, pady=5)

        # Input Image Display
        self.input_canvas = tk.Canvas(self.master, width=400, height=400, bg='white')
        self.input_canvas.grid(row=1, column=0, padx=5, pady=5)
        self.input_canvas.bind("<Button-1>", self.on_click)
        self.input_canvas.bind("<B1-Motion>", self.on_drag)
        self.input_canvas.bind("<ButtonRelease-1>", self.on_release)
        self.selected_point = None
        self.selected_point_index = -1

        # Output Image Display
        self.output_canvas = tk.Canvas(self.master, width=400, height=400, bg='white')
        self.output_canvas.grid(row=1, column=1, padx=5, pady=5)

        # Mesh Grid Controls
        controls_frame = ttk.Frame(self.master)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=10)

        rows_label = ttk.Label(controls_frame, text="Rows:")
        rows_label.grid(row=0, column=0, padx=5)
        self.rows_entry = ttk.Entry(controls_frame, width=5)
        self.rows_entry.insert(0, "5")
        self.rows_entry.grid(row=0, column=1, padx=5)

        cols_label = ttk.Label(controls_frame, text="Cols:")
        cols_label.grid(row=0, column=2, padx=5)
        self.cols_entry = ttk.Entry(controls_frame, width=5)
        self.cols_entry.insert(0, "5")
        self.cols_entry.grid(row=0, column=3, padx=5)

        resize_button = ttk.Button(controls_frame, text="Resize Grid", command=self.resize_grid)
        resize_button.grid(row=0, column=4, padx=20)

        # Output Dimensions
        width_label = ttk.Label(controls_frame, text="Output Width:")
        width_label.grid(row=1, column=0, padx=5, pady=10)
        self.width_entry = ttk.Entry(controls_frame, width=5)
        self.width_entry.insert(0, "400")
        self.width_entry.grid(row=1, column=1, padx=5)

        height_label = ttk.Label(controls_frame, text="Output Height:")
        height_label.grid(row=1, column=2, padx=5)
        self.height_entry = ttk.Entry(controls_frame, width=5)
        self.height_entry.insert(0, "400")
        self.height_entry.grid(row=1, column=3, padx=5)

        update_button = ttk.Button(controls_frame, text="Update", command=self.update_image)
        update_button.grid(row=1, column=4, padx=20)

        # Save/Load Buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        save_mesh_button = ttk.Button(button_frame, text="Save Mesh", command=self.save_mesh)
        save_mesh_button.grid(row=0, column=0, padx=5)

        load_mesh_button = ttk.Button(button_frame, text="Load Mesh", command=self.load_mesh)
        load_mesh_button.grid(row=0, column=1, padx=5)

        save_result_button = ttk.Button(button_frame, text="Save Result", command=self.save_result)
        save_result_button.grid(row=0, column=2, padx=5)

        save_maps_button = ttk.Button(button_frame, text="Save Maps", command=self.save_maps)
        save_maps_button.grid(row=0, column=3, padx=5)

        # Status Bar
        self.status_bar = ttk.Label(self.master, text="")
        self.status_bar.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

    def load_image(self, filepath=None):
        if filepath is None:
            filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        
        if filepath:
            try:
                print(f"Loading image from: {filepath}")
                self.input_image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                if self.input_image is None:
                    raise Exception(f"Failed to load image from {filepath}")
                
                print(f"Image loaded successfully, shape: {self.input_image.shape}")
                self.display_image(self.input_image, self.input_canvas)
                print("Image displayed")
                self.initialize_mesh_grid()
                print("Mesh grid initialized")
                self.status_bar.config(text=f"Loaded image: {filepath}")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.status_bar.config(text=f"Error loading image: {e}")
                import traceback
                traceback.print_exc()

    def initialize_mesh_grid(self):
        if self.input_image is None:
            return
            
        rows = int(self.rows_entry.get())
        cols = int(self.cols_entry.get())
        h, w = self.input_image.shape[:2]
        
        # Create regular grid
        x = np.linspace(0, w-1, cols+1)
        y = np.linspace(0, h-1, rows+1)
        xv, yv = np.meshgrid(x, y)
        
        # Store as mesh points
        self.mesh_points = []
        for i in range(rows + 1):
            for j in range(cols + 1):
                self.mesh_points.append((int(xv[i,j]), int(yv[i,j])))
                
        self.draw_mesh()

    def resize_grid(self):
        if self.input_image is not None:
            self.initialize_mesh_grid()
            self.update_image()

    def draw_mesh(self):
        if not self.mesh_points:
            return
            
        self.input_canvas.delete("mesh")
        rows = int(self.rows_entry.get())
        cols = int(self.cols_entry.get())
        
        # Draw horizontal lines
        for r in range(rows + 1):
            for c in range(cols):
                idx1 = r * (cols + 1) + c
                idx2 = r * (cols + 1) + c + 1
                if idx1 < len(self.mesh_points) and idx2 < len(self.mesh_points):
                    x1, y1 = self.mesh_points[idx1]
                    x2, y2 = self.mesh_points[idx2]
                    self.input_canvas.create_line(x1, y1, x2, y2, fill="blue", tags="mesh")

        # Draw vertical lines
        for c in range(cols + 1):
            for r in range(rows):
                idx1 = r * (cols + 1) + c
                idx2 = (r + 1) * (cols + 1) + c
                if idx1 < len(self.mesh_points) and idx2 < len(self.mesh_points):
                    x1, y1 = self.mesh_points[idx1]
                    x2, y2 = self.mesh_points[idx2]
                    self.input_canvas.create_line(x1, y1, x2, y2, fill="blue", tags="mesh")

        # Draw points with coordinates
        for i, (x, y) in enumerate(self.mesh_points):
            r = i // (cols + 1)
            c = i % (cols + 1)
            self.input_canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", tags="mesh")
            self.input_canvas.create_text(x, y-10, text=f"({r},{c})", tags="mesh", font=("Arial", 8))

    def update_image(self):
        if self.input_image is not None and self.mesh_points:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            output_width = int(self.width_entry.get())
            output_height = int(self.height_entry.get())

            # Create mapX and mapY
            self.mapX = np.zeros((output_height, output_width), dtype=np.float32)
            self.mapY = np.zeros((output_height, output_width), dtype=np.float32)

            # Convert mesh points to numpy arrays for interpolation
            src_points = np.float32(self.mesh_points).reshape(rows+1, cols+1, 2)
            dst_points = np.zeros((rows+1, cols+1, 2), dtype=np.float32)
            
            # Create regular grid in destination
            for i in range(rows+1):
                for j in range(cols+1):
                    dst_points[i,j] = [j * output_width/cols, i * output_height/rows]

            # Interpolate the mapping
            for i in range(output_height):
                for j in range(output_width):
                    # Find the corresponding source point
                    x = j * cols / output_width
                    y = i * rows / output_height
                    
                    # Get the four surrounding points
                    x0, y0 = int(x), int(y)
                    x1, y1 = min(x0 + 1, cols), min(y0 + 1, rows)
                    
                    # Bilinear interpolation weights
                    wx = x - x0
                    wy = y - y0
                    
                    # Get source points
                    p00 = src_points[y0, x0]
                    p01 = src_points[y0, x1]
                    p10 = src_points[y1, x0]
                    p11 = src_points[y1, x1]
                    
                    # Interpolate
                    point = (1-wy)*((1-wx)*p00 + wx*p01) + wy*((1-wx)*p10 + wx*p11)
                    
                    self.mapX[i,j] = point[0]
                    self.mapY[i,j] = point[1]

            self.output_image = cv2.remap(self.input_image, self.mapX, self.mapY, cv2.INTER_LINEAR)
            self.display_image(self.output_image, self.output_canvas)

    def on_click(self, event):
        if self.input_image is not None:
            self.selected_point = self.find_closest_point(event.x, event.y)
            if self.selected_point:
                r = self.selected_point_index // (int(self.cols_entry.get()) + 1)
                c = self.selected_point_index % (int(self.cols_entry.get()) + 1)
                self.status_bar.config(text=f"Selected point: ({self.selected_point[0]}, {self.selected_point[1]}) at grid position (row={r}, col={c})")
        else:
            self.status_bar.config(text="Load an image first.")

    def on_drag(self, event):
        if self.selected_point is not None and self.selected_point_index >= 0:
            h, w = self.input_image.shape[:2]
            new_x = max(0, min(event.x, w - 1))
            new_y = max(0, min(event.y, h - 1))
            self.mesh_points[self.selected_point_index] = (new_x, new_y)
            r = self.selected_point_index // (int(self.cols_entry.get()) + 1)
            c = self.selected_point_index % (int(self.cols_entry.get()) + 1)
            self.status_bar.config(text=f"Moving point to: ({new_x}, {new_y}) at grid position (row={r}, col={c})")
            self.draw_mesh()

    def on_release(self, event):
        if self.selected_point is not None:
            self.update_image()
            self.selected_point = None
            self.selected_point_index = -1

    def find_closest_point(self, x, y):
        if self.mesh_points:
            min_dist = float('inf')
            closest_point = None
            closest_index = -1
            for i, (px, py) in enumerate(self.mesh_points):
                dist = ((x - px)**2 + (y - py)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_point = (px, py)
                    closest_index = i
            if min_dist < 10:  # Only select point if within 10 pixels
                self.selected_point_index = closest_index
                return closest_point
        return None

    def display_image(self, image, canvas):
        h, w = image.shape[:2]
        canvas.config(width=w, height=h)
        # Convert OpenCV grayscale image to PIL format
        image_pil = Image.fromarray(image).convert('L')
        # Convert PIL image to PhotoImage
        photo = ImageTk.PhotoImage(image=image_pil)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo  # Keep a reference

    def save_mesh(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                              filetypes=[("JSON files", "*.json")])
        if filepath:
            data = {
                "mesh_points": self.mesh_points,
                "rows": int(self.rows_entry.get()),
                "cols": int(self.cols_entry.get())
            }
            with open(filepath, "w") as f:
                json.dump(data, f)
            self.status_bar.config(text=f"Mesh saved to: {filepath}")

    def load_mesh(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            with open(filepath, "r") as f:
                data = json.load(f)
                self.mesh_points = data["mesh_points"]
                self.rows_entry.delete(0, tk.END)
                self.rows_entry.insert(0, str(data["rows"]))
                self.cols_entry.delete(0, tk.END)
                self.cols_entry.insert(0, str(data["cols"]))
                self.draw_mesh()
                self.update_image()
            self.status_bar.config(text=f"Mesh loaded from: {filepath}")

    def save_result(self):
        if self.output_image is not None:
            filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=[("PNG files", "*.png"),
                                                           ("JPEG files", "*.jpg"),
                                                           ("All files", "*.*")])
            if filepath:
                cv2.imwrite(filepath, self.output_image)
                self.status_bar.config(text=f"Result image saved to: {filepath}")

    def save_maps(self):
        if self.mapX is not None and self.mapY is not None:
            filepath = filedialog.asksaveasfilename(defaultextension=".npz",
                                                  filetypes=[("NumPy files", "*.npz")])
            if filepath:
                np.savez(filepath, mapX=self.mapX, mapY=self.mapY)
                self.status_bar.config(text=f"Map files saved to: {filepath}")

root = tk.Tk()
app = MeshWarpApp(root)
root.mainloop()
