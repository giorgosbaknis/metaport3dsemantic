# Bounding Box Processing and Mesh Export

This repository contains two Python scripts for processing GLB files to extract room and object bounding boxes, and for exporting these bounding boxes into PLY files. The scripts work in sequence to generate a structured JSON file from the GLB files and then create PLY mesh files based on the bounding boxes specified in the JSON files.

## Programs Overview

### 1. **GLB to JSON Structure Conversion**

This program processes multiple folders, each containing a `.glb` and a corresponding `.txt` file, to generate a structured JSON file with information about room and object bounding boxes.

**Workflow:**
- Converts the `.glb` file into an `.obj` file using `trimesh`.
- Parses the `.obj` and `.txt` files to extract and organize bounding box information.
- Saves the extracted information into a structured JSON file in the same folder.

**Usage:**
```python
# Run the script to process all folders
process_all_folders('/path/to/root_directory')
