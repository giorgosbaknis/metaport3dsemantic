# Bounding Box Processing and Mesh Export

This repository contains two Python scripts for processing GLB files to extract room and object bounding boxes, and for exporting these bounding boxes into PLY files. The scripts work in sequence to generate a structured JSON file from the GLB files and then create PLY mesh files based on the bounding boxes specified in the JSON files.

## Overview

### 1. **GLB to JSON Structure Conversion**

This script processes directories containing `.glb` and `.txt` files to produce structured JSON files. The JSON files contain comprehensive data about the rooms and objects within the 3D models, including their bounding boxes.

**Detailed Workflow:**
- **Step 1:** Convert the `.glb` file to an `.obj` file using the `trimesh` library.
- **Step 2:** Parse the `.obj` file to extract vertex and texture information.
- **Step 3:** Parse the `.txt` file (semantic annotations) to associate vertices with specific rooms and objects.
- **Step 4:** Calculate the bounding boxes for each room and each object based on their vertices.
- **Step 5:** Organize the extracted data into a JSON structure, including:
  - Building name (derived from the folder name)
  - Number of rooms in the building
  - List of rooms, each containing:
    - Room ID
    - Room bounding box
    - List of objects, each containing:
      - Object ID
      - Object name
      - Object color (in hexadecimal format)
      - Object bounding box
- **Step 6:** Save the JSON file in the same folder as the input files.

**JSON Structure Example:**
```json
{
  "building_name": "00800-TEEsavR23oF",
  "number_of_rooms": 3,
  "rooms": [
    {
      "room_id": "1",
      "room_bounding_box": {
        "min": [0.0, 0.0, 0.0],
        "max": [10.0, 10.0, 10.0]
      },
      "objects": [
        {
          "object_id": "1",
          "object_name": "chair",
          "hex_color": "FF5733",
          "bounding_box": {
            "min": [1.0, 1.0, 1.0],
            "max": [2.0, 2.0, 2.0]
          }
        },
        ...
      ]
    },
    ...
  ]
}

