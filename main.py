import os
import trimesh
from PIL import Image
import json

def load_material_images(material_filenames, folder_path='.'):
    images = {}
    for filename in material_filenames:
        file_path = os.path.join(folder_path, filename)
        if filename not in images:  # Load the image only if it hasn't been loaded yet
            try:
                img = Image.open(file_path)
                images[filename] = img.convert('RGB')  # Ensure the image is in RGB mode
                print(f"Loaded {filename}")
            except FileNotFoundError:
                print(f"Error: {filename} not found.")
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return images

def texture_coordinate_to_hex(texture_coordinate, image):
    width, height = image.size
    u, v = texture_coordinate
    x = int(u * (width - 1))
    y = int((1 - v) * (height - 1))
    r, g, b = image.getpixel((x, y))
    hex_color = '{:02x}{:02x}{:02x}'.format(r, g, b).upper()
    return hex_color

def compare_color(texture_coordinate, image, target_hex_color):
    extracted_hex_color = texture_coordinate_to_hex(texture_coordinate, image)
    return extracted_hex_color == target_hex_color.upper()

def calculate_bounding_box(vertices):
    min_x, min_y, min_z = vertices[0]
    max_x, max_y, max_z = vertices[0]

    for x, y, z in vertices[1:]:
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        min_z = min(min_z, z)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        max_z = max(max_z, z)

    return (min_x, min_y, min_z), (max_x, max_y, max_z)

def parse_obj_file(obj_file):
    vertices = []
    texture_coords = []
    material_filenames = []

    material_filename = ""
    with open(obj_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            tokens = line.split()
            first_token = tokens[0]

            if first_token == 'usemtl':
                material_filename = f"{tokens[1]}.png"
            elif first_token == 'v':
                vertex = tuple(map(float, tokens[1:4]))
                vertices.append(vertex)
                material_filenames.append(material_filename)
            elif first_token == 'vt':
                texture_coord = tuple(map(float, tokens[1:3]))
                texture_coords.append(texture_coord)

    return vertices, texture_coords, material_filenames

def filter_vertices_by_color(vertices, texture_coords, material_filenames, target_hex_color, images):
    filtered_vertices = []
    for i in range(len(vertices)):
        vertex = vertices[i]
        texture_coord = texture_coords[i]
        material_filename = material_filenames[i]
        image = images.get(material_filename)
        if image and compare_color(texture_coord, image, target_hex_color):
            filtered_vertices.append(vertex)
    return filtered_vertices

def save_bounding_box_as_lines_to_ply(bounding_box, ply_filename):
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
        (0, 4), (1, 5), (2, 6), (3, 7),  # Vertical edges
    ]

    with open(ply_filename, 'w') as file:
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write(f"element vertex {len(vertices)}\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write(f"element edge {len(edges)}\n")
        file.write("property int vertex1\n")
        file.write("property int vertex2\n")
        file.write("end_header\n")

        for vertex in vertices:
            file.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")

        for edge in edges:
            file.write(f"{edge[0]} {edge[1]}\n")

def parse_semantic_annotations(file_path):
    objects_by_room = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            parts = line.strip().split(',')
            obj_id = parts[0]
            hex_color = parts[1]
            obj_name = parts[2].strip('"')
            room_id = parts[3]

            if room_id not in objects_by_room:
                objects_by_room[room_id] = []

            objects_by_room[room_id].append({
                'object_id': obj_id,
                'hex_color': hex_color,
                'object_name': obj_name
            })

    return objects_by_room

def combine_bounding_boxes_to_ply(bounding_boxes, ply_filename):
    all_vertices = []
    all_edges = []
    vertex_offset = 0

    for bounding_box in bounding_boxes:
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
            (0 + vertex_offset, 1 + vertex_offset), (1 + vertex_offset, 3 + vertex_offset),
            (3 + vertex_offset, 2 + vertex_offset), (2 + vertex_offset, 0 + vertex_offset),
            (4 + vertex_offset, 5 + vertex_offset), (5 + vertex_offset, 7 + vertex_offset),
            (7 + vertex_offset, 6 + vertex_offset), (6 + vertex_offset, 4 + vertex_offset),
            (0 + vertex_offset, 4 + vertex_offset), (1 + vertex_offset, 5 + vertex_offset),
            (2 + vertex_offset, 6 + vertex_offset), (3 + vertex_offset, 7 + vertex_offset),
        ]
        all_vertices.extend(vertices)
        all_edges.extend(edges)
        vertex_offset += 8

    with open(ply_filename, 'w') as file:
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write(f"element vertex {len(all_vertices)}\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write(f"element edge {len(all_edges)}\n")
        file.write("property int vertex1\n")
        file.write("property int vertex2\n")
        file.write("end_header\n")

        for vertex in all_vertices:
            file.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")

        for edge in edges:
            file.write(f"{edge[0]} {edge[1]}\n")

def group_vertices_by_color(vertices, texture_coords, material_filenames, images):
    grouped_vertices = {}
    for i in range(len(vertices)):
        vertex = vertices[i]
        texture_coord = texture_coords[i]
        material_filename = material_filenames[i]
        image = images.get(material_filename)
        if image:
            hex_color = texture_coordinate_to_hex(texture_coord, image)
            if hex_color not in grouped_vertices:
                grouped_vertices[hex_color] = []
            grouped_vertices[hex_color].append(vertex)
    return grouped_vertices

def create_room_objects_dict(objects_by_room, grouped_vertices):
    room_objects_dict = {}

    for room_id, objects in objects_by_room.items():
        room_objects_dict[room_id] = []

        for obj in objects:
            hex_color = obj['hex_color']
            if hex_color in grouped_vertices:
                bounding_box = calculate_bounding_box(grouped_vertices[hex_color])
                room_objects_dict[room_id].append({
                    'object_id': obj['object_id'],
                    'object_name': obj['object_name'],
                    'hex_color': hex_color,
                    'bounding_box': bounding_box
                })

    return room_objects_dict

def create_room_bounding_boxes(room_objects_dict, grouped_vertices):
    room_bounding_boxes = {}

    for room_id, objects in room_objects_dict.items():
        room_vertices = []

        for obj in objects:
            hex_color = obj['hex_color']
            if hex_color in grouped_vertices:
                room_vertices.extend(grouped_vertices[hex_color])

        if room_vertices:
            room_bounding_box = calculate_bounding_box(room_vertices)
            room_bounding_boxes[room_id] = room_bounding_box

    return room_bounding_boxes

def save_room_bounding_boxes_to_ply(room_bounding_boxes, output_folder):
    bounding_boxes = list(room_bounding_boxes.values())

    if bounding_boxes:
        ply_filename = os.path.join(output_folder, 'rooms_bounding_boxes.ply')
        combine_bounding_boxes_to_ply(bounding_boxes, ply_filename)
        print(f"Room bounding boxes saved to {ply_filename}")
    else:
        print("No room bounding boxes to save.")

def save_room_objects_dict_to_json(room_objects_dict, output_folder):
    json_filename = os.path.join(output_folder, 'room_objects.json')

    with open(json_filename, 'w') as json_file:
        json.dump(room_objects_dict, json_file, indent=4)

    print(f"Room objects dictionary saved to {json_filename}")

def add_room_bounding_boxes_to_dict(room_objects_dict, grouped_vertices):
    for room_id, objects in room_objects_dict.items():
        room_vertices = []

        for obj in objects:
            hex_color = obj['hex_color']
            if hex_color in grouped_vertices:
                room_vertices.extend(grouped_vertices[hex_color])

        if room_vertices:
            room_bounding_box = calculate_bounding_box(room_vertices)
            room_objects_dict[room_id].append({
                'room_bounding_box': room_bounding_box
            })

    return room_objects_dict

def save_building_structure_to_json(room_objects_dict, output_folder, building_name):
    building_structure = {
        "building_name": building_name,
        "number_of_rooms": len(room_objects_dict),
        "rooms": []
    }

    for room_id, objects in room_objects_dict.items():
        room_data = {
            "room_id": room_id,
            "room_bounding_box": objects[-1]["room_bounding_box"],
            "objects": []
        }

        for obj in objects[:-1]:  # Exclude the room bounding box entry
            room_data["objects"].append({
                "object_id": obj["object_id"],
                "object_name": obj["object_name"],
                "hex_color": obj["hex_color"],
                "bounding_box": obj["bounding_box"]
            })

        building_structure["rooms"].append(room_data)

    json_filename = os.path.join(output_folder, f'{building_name}_structure.json')

    with open(json_filename, 'w') as json_file:
        json.dump(building_structure, json_file, indent=4)

    print(f"Building structure saved to {json_filename}")

def process_objects(obj_file, annotations_file, output_folder, texture_folder='.'):
    os.makedirs(output_folder, exist_ok=True)
    objects_by_room = parse_semantic_annotations(annotations_file)
    vertices, texture_coords, material_filenames = parse_obj_file(obj_file)

    images = load_material_images(set(material_filenames), texture_folder)

    grouped_vertices = group_vertices_by_color(vertices, texture_coords, material_filenames, images)

    room_objects_dict = create_room_objects_dict(objects_by_room, grouped_vertices)

    room_objects_dict = add_room_bounding_boxes_to_dict(room_objects_dict, grouped_vertices)

    save_building_structure_to_json(room_objects_dict, output_folder, os.path.basename(output_folder))

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    base_file_name = folder_name.split('-')[-1]
    glb_file = os.path.join(folder_path, f"{base_file_name}.semantic.glb")
    semantic_file = os.path.join(folder_path, f"{base_file_name}.semantic.txt")

    if not os.path.isfile(glb_file) or not os.path.isfile(semantic_file):
        print(f"Missing required files in {folder_path}. Skipping this folder.")
        return

    scene = trimesh.load(glb_file)
    obj_file = os.path.join(folder_path, 'output_file.obj')
    scene.export(obj_file)
    print(f"Converted {glb_file} to {obj_file}")

    process_objects(obj_file, semantic_file, folder_path, texture_folder=folder_path)
    print(f"Processed {folder_path} and saved JSON output.")

def process_all_folders(root_folder):
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)

# Usage example
root_directory = '.'  # Specify the root directory containing all the folders
process_all_folders(root_directory)
