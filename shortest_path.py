import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import networkx as nx
import sys


def load_height_map(file_path):
    with open(file_path, 'rb') as file:
        height_data = np.fromfile(file, dtype=np.uint8)
    return height_data.reshape(512, 512).astype(np.float64)


# Spatial resolution and height value conversion factors
spatial_resolution = 30  # meters per pixel
height_resolution = 11   # meters per height value

def generate_graph_with_heights(height_map, height_resolution, spatial_resolution):
    rows, cols = height_map.shape
    G = nx.Graph()
    # Generate the Delaunay triangulation
    x = np.arange(cols) 
    y = np.arange(rows)
    X, Y = np.meshgrid(x, y)
    points = np.vstack([X.ravel(), Y.ravel()]).T
    tri = Delaunay(points)

    # Add nodes and edges based on the triangulation
    for simplex in tri.simplices:
        for i in range(3):
            for j in range(i+1, 3):
                p1, p2 = simplex[i], simplex[j]
                # Convert indices to (row, col) coordinates
                row1, col1 = int(points[p1][1]), int(points[p1][0])
                row2, col2 = int(points[p2][1]), int(points[p2][0])
                # Calculate weight using height difference
                weight = abs(height_map[row1, col1] - height_map[row2, col2]) * height_resolution * spatial_resolution
                G.add_edge((row1, col1), (row2, col2), weight=weight)

    return G

# Load pre-eruption and post-eruption height maps
pre_eruption_height_map = load_height_map("pre.data")
post_eruption_height_map = load_height_map("post.data")

# Specify points A and B in pixel coordinates (x, y)
# Get points A and B from command-line arguments
try:
    start = tuple(map(int, sys.argv[1].split(',')))
    end = tuple(map(int, sys.argv[2].split(',')))
except IndexError:
    print("Please provide the coordinates of points A and B in the format 'x,y'")
    sys.exit(1)


def path_for_eruption(height_map):
    G = generate_graph_with_heights(height_map, height_resolution, spatial_resolution)
    shortest_path = nx.shortest_path(G, source=start, target=end, weight='weight')
    path_length = nx.shortest_path_length(G, source=start, target=end, weight='weight')
    #print("Path length:", path_length, "meters")
    return path_length, shortest_path

pre_eruption_path_length = path_for_eruption(pre_eruption_height_map)
post_eruption_path_length = path_for_eruption(post_eruption_height_map)

print("Difference of path lengths: ", pre_eruption_path_length[0] - post_eruption_path_length[0], "Meters")


def plot_path(height_map, path):
    plt.figure(figsize=(8, 8))
    plt.imshow(height_map, cmap='terrain', origin='upper')
    plt.colorbar(label='Height (m)')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('Terrain Map with Shortest Path')
    path_array = np.array(path)
    plt.plot(path_array[:, 1], path_array[:, 0], color='red', linewidth=2)
    plt.show()

#plot_path(pre_eruption_height_map, pre_eruption_path_length[1])
plot_path(post_eruption_height_map, post_eruption_path_length[1])
