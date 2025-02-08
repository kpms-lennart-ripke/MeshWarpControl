import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class MeshPoint:
    x: float  # Changed to float for subpixel precision
    y: float  # Changed to float for subpixel precision
    row: int
    col: int

class MeshGrid:
    def __init__(self, rows: int, cols: int, image_height: int, image_width: int, border_percentage: float = 0.1):
        self.rows = rows
        self.cols = cols
        self.points: List[List[MeshPoint]] = []
        self.initialize_grid(image_height, image_width, border_percentage)

    def initialize_grid(self, image_height: int, image_width: int, border_percentage: float):
        border_h = int(image_height * border_percentage)
        border_w = int(image_width * border_percentage)
        
        # Create regular grid
        x = np.linspace(border_w, image_width - border_w, self.cols + 1)
        y = np.linspace(border_h, image_height - border_h, self.rows + 1)
        xv, yv = np.meshgrid(x, y)
        
        # Convert to MeshPoint objects organized by rows
        self.points = []
        for r in range(self.rows + 1):
            row_points = []
            for c in range(self.cols + 1):
                point = MeshPoint(
                    x=float(xv[r, c]),  # Convert to float for subpixel precision
                    y=float(yv[r, c]),  # Convert to float for subpixel precision
                    row=r,
                    col=c
                )
                row_points.append(point)
            self.points.append(row_points)

    def get_point(self, row: int, col: int) -> MeshPoint:
        return self.points[row][col]

    def set_point(self, row: int, col: int, x: float, y: float):  # Changed to float
        self.points[row][col].x = x
        self.points[row][col].y = y

    def get_all_points(self) -> List[Tuple[float, float]]:  # Changed return type
        """Returns flattened list of (x,y) coordinates for compatibility"""
        points = []
        for row in self.points:
            for point in row:
                points.append((point.x, point.y))
        return points

    def to_dict(self) -> dict:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "points": [[{"x": p.x, "y": p.y} for p in row] for row in self.points]
        }

    @classmethod
    def from_dict(cls, data: dict, image_height: int, image_width: int) -> 'MeshGrid':
        mesh = cls(data["rows"], data["cols"], image_height, image_width, border_percentage=0)
        mesh.points = []
        for r, row_data in enumerate(data["points"]):
            row_points = []
            for c, point_data in enumerate(row_data):
                point = MeshPoint(
                    x=float(point_data["x"]),  # Convert to float
                    y=float(point_data["y"]),  # Convert to float
                    row=r,
                    col=c
                )
                row_points.append(point)
            mesh.points.append(row_points)
        return mesh

    def get_maps(self, output_width: int, output_height: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate mapX and mapY for cv2.remap"""
        mapX = np.zeros((output_height, output_width), dtype=np.float32)
        mapY = np.zeros((output_height, output_width), dtype=np.float32)

        # Convert mesh points to numpy arrays for interpolation
        src_points = np.array([[(p.x, p.y) for p in row] for row in self.points], dtype=np.float32)
        
        # Create regular grid in destination
        dst_points = np.zeros((self.rows+1, self.cols+1, 2), dtype=np.float32)
        for i in range(self.rows+1):
            for j in range(self.cols+1):
                dst_points[i,j] = [j * output_width/self.cols, i * output_height/self.rows]

        # Interpolate the mapping
        for i in range(output_height):
            for j in range(output_width):
                # Find the corresponding source point
                x = j * self.cols / output_width
                y = i * self.rows / output_height
                
                # Get the four surrounding points
                x0, y0 = int(x), int(y)
                x1, y1 = min(x0 + 1, self.cols), min(y0 + 1, self.rows)
                
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
                
                mapX[i,j] = point[0]
                mapY[i,j] = point[1]

        return mapX, mapY
