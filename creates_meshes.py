import os
import json
import numpy as np

def create_ply_file(vertices, edges, output_file):
    with open(output_file, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(vertices)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write(f"element edge {len(edges)}\n")
        f.write("property int vertex1\n")
        f.write("property int vertex2\n")
        f.write("end_header\n")
        
        for vertex in vertices:
            f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")
        
        for edge in edges:
            f.write(f"{edge[0]} {edge[1]}\n")

def bounding_box_to_vertices_and_edges(bounding_box):
    min_point, max_point = bounding_box
    vertices = [
        min_point,
        (min_point[0], min_point[1], max_point[2]),
        (min_point[0], max_point[1], min_point[2]),
        (min_point[0], max_point[1], max_point[2]),
        (max_point[0], min_point[1], min_point[2]),
        (max_point[0], min_point[1], max_point[2]),
        (max_point[0], max_point[1], min_point[2]),
        max_point,
    ]
    
    edges = [
        (0, 1), (1, 3), (3, 2), (2, 0),  # Bottom face edges
        (4, 5), (5, 7), (7, 6), (6, 4),  # Top face edges
        (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
    ]
    
    return vertices, edges

def process_json_file(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    room_vertices = []
    room_edges = []
    object_vertices = []
    object_edges = []
    
    for room in data['rooms']:
        # Process room bounding box
        room_bbox = room['room_bounding_box']
        room_v, room_e = bounding_box_to_vertices_and_edges(room_bbox)
        room_vertices.extend(room_v)
        room_edges.extend([(edge[0] + len(room_vertices) - 8, edge[1] + len(room_vertices) - 8) for edge in room_e])
        
        # Process object bounding boxes
        for obj in room['objects']:
            obj_bbox = obj['bounding_box']
            obj_v, obj_e = bounding_box_to_vertices_and_edges(obj_bbox)
            object_vertices.extend(obj_v)
            object_edges.extend([(edge[0] + len(object_vertices) - 8, edge[1] + len(object_vertices) - 8) for edge in obj_e])
    
    return room_vertices, room_edges, object_vertices, object_edges

def process_folder_for_ply_files(folder_path):
    json_file_name = os.path.basename(folder_path) + '_structure.json'
    json_file_path = os.path.join(folder_path, json_file_name)

    if not os.path.isfile(json_file_path):
        print(f"No JSON file found in {folder_path}. Skipping this folder.")
        return

    room_vertices, room_edges, object_vertices, object_edges = process_json_file(json_file_path)

    # Save room bounding boxes to PLY
    room_ply_file = os.path.join(folder_path, 'room_bounding_boxes.ply')
    create_ply_file(room_vertices, room_edges, room_ply_file)
    print(f"Room bounding boxes saved to {room_ply_file}")

    # Save object bounding boxes to PLY
    object_ply_file = os.path.join(folder_path, 'object_bounding_boxes.ply')
    create_ply_file(object_vertices, object_edges, object_ply_file)
    print(f"Object bounding boxes saved to {object_ply_file}")

def process_all_folders_for_ply(root_folder):
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            process_folder_for_ply_files(folder_path)

# Usage example
root_directory = '.'  # Specify the root directory containing all the folders
process_all_folders_for_ply(root_directory)
