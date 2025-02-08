import cv2
import numpy as np
import json
import os
from typing import Optional, Tuple, Callable
from models.mesh_grid import MeshGrid, MeshPoint

class MeshWarpViewModel:
    def __init__(self):
        self.input_image: Optional[np.ndarray] = None
        self.output_image: Optional[np.ndarray] = None
        self.mesh_grid: Optional[MeshGrid] = None
        self.mapX: Optional[np.ndarray] = None
        self.mapY: Optional[np.ndarray] = None
        
        # Callbacks for view updates
        self.on_input_image_changed: Optional[Callable[[np.ndarray], None]] = None
        self.on_output_image_changed: Optional[Callable[[np.ndarray], None]] = None
        self.on_mesh_updated: Optional[Callable[[], None]] = None
        self.on_status_changed: Optional[Callable[[str], None]] = None

    def load_image(self, filepath: str) -> bool:
        try:
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise Exception(f"Failed to load image from {filepath}")
            
            self.input_image = image
            if self.on_input_image_changed:
                self.on_input_image_changed(self.input_image)
                
            self.initialize_mesh_grid()
            self.update_output_image()  # Update output image immediately after loading
            return True
        except Exception as e:
            if self.on_status_changed:
                self.on_status_changed(f"Error loading image: {e}")
            return False

    def initialize_mesh_grid(self, rows: int = 5, cols: int = 5):
        if self.input_image is None:
            return
            
        h, w = self.input_image.shape[:2]
        self.mesh_grid = MeshGrid(rows, cols, h, w)
        
        if self.on_mesh_updated:
            self.on_mesh_updated()

    def resize_grid(self, rows: int, cols: int):
        if self.input_image is None:
            return
            
        h, w = self.input_image.shape[:2]
        self.mesh_grid = MeshGrid(rows, cols, h, w)
        
        if self.on_mesh_updated:
            self.on_mesh_updated()
        
        self.update_output_image()

    def move_point(self, row: int, col: int, x: int, y: int):
        if self.mesh_grid is None:
            return
            
        h, w = self.input_image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        
        self.mesh_grid.set_point(row, col, x, y)
        
        if self.on_mesh_updated:
            self.on_mesh_updated()

    def update_output_image(self, output_width: Optional[int] = None, output_height: Optional[int] = None):
        if self.input_image is None or self.mesh_grid is None:
            return
            
        if output_width is None:
            output_width = self.input_image.shape[1]
        if output_height is None:
            output_height = self.input_image.shape[0]

        self.mapX, self.mapY = self.mesh_grid.get_maps(output_width, output_height)
        self.output_image = cv2.remap(self.input_image, self.mapX, self.mapY, cv2.INTER_LINEAR)
        
        if self.on_output_image_changed:
            self.on_output_image_changed(self.output_image)

    def save_mesh(self, filepath: str) -> bool:
        if self.mesh_grid is None:
            if self.on_status_changed:
                self.on_status_changed("No mesh to save")
            return False
            
        try:
            data = self.mesh_grid.to_dict()
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
                
            if self.on_status_changed:
                self.on_status_changed(f"Mesh saved to: {filepath}")
            return True
        except Exception as e:
            if self.on_status_changed:
                self.on_status_changed(f"Error saving mesh: {e}")
            return False

    def load_mesh(self, filepath: str) -> bool:
        if self.input_image is None:
            if self.on_status_changed:
                self.on_status_changed("Load an image first")
            return False
            
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            h, w = self.input_image.shape[:2]
            self.mesh_grid = MeshGrid.from_dict(data, h, w)
            
            if self.on_mesh_updated:
                self.on_mesh_updated()
                
            self.update_output_image()
            
            if self.on_status_changed:
                self.on_status_changed(f"Mesh loaded from: {filepath}")
            return True
        except Exception as e:
            if self.on_status_changed:
                self.on_status_changed(f"Error loading mesh: {e}")
            return False

    def save_result(self, filepath: str) -> bool:
        if self.output_image is None:
            if self.on_status_changed:
                self.on_status_changed("No result image to save")
            return False
            
        try:
            cv2.imwrite(filepath, self.output_image)
            if self.on_status_changed:
                self.on_status_changed(f"Result image saved to: {filepath}")
            return True
        except Exception as e:
            if self.on_status_changed:
                self.on_status_changed(f"Error saving result: {e}")
            return False

    def save_maps(self, filepath: str) -> bool:
        if self.mapX is None or self.mapY is None:
            if self.on_status_changed:
                self.on_status_changed("No maps to save")
            return False
            
        try:
            np.savez(filepath, mapX=self.mapX, mapY=self.mapY)
            if self.on_status_changed:
                self.on_status_changed(f"Maps saved to: {filepath}")
            return True
        except Exception as e:
            if self.on_status_changed:
                self.on_status_changed(f"Error saving maps: {e}")
            return False

    def get_point_info(self, x: int, y: int, max_distance: int = 10) -> Optional[Tuple[MeshPoint, float]]:
        """Find closest mesh point within max_distance pixels"""
        if self.mesh_grid is None:
            return None
            
        closest_point = None
        min_dist = float('inf')
        
        for row in self.mesh_grid.points:
            for point in row:
                dist = ((x - point.x)**2 + (y - point.y)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_point = point
                    
        if min_dist <= max_distance:
            return closest_point, min_dist
        return None
