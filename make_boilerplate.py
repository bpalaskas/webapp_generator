import json
import os
import base64
from get_boilerplate import write_boilerplate_content
def convert_folder_structure(folder_structure_path):
    with open(folder_structure_path, 'r') as fs_file:
        folder_structure_data = json.load(fs_file)

    converted_data = []

    #recursion
    def traverse_structure(structure, path=''):
        if 'files' in structure:
            for file_name in structure['files']:
                file_path = os.path.join(path, file_name)
                converted_data.append({"name": file_name, "content": "", "path": file_path})
        for folder_name, sub_structure in structure.items():
            if folder_name != 'files':
                traverse_structure(sub_structure, os.path.join(path, folder_name))

    traverse_structure(folder_structure_data)

    return converted_data

def write_contents_to_files(data, base_directory):
    if not isinstance(data, list):
        raise ValueError("Input data should be a list of dictionaries.")
    base_directory = os.path.normpath(base_directory)

    for obj in data:
        name = obj.get("name")
        content = obj.get("content", "")
        rel_path = obj.get("path")

        if not all([name, rel_path]):
            print(f"Object {name} does not have a valid 'name' or 'path'.")
            continue

        full_path = os.path.join(base_directory, rel_path)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the content to the file, overwriting if it exists
        with open(full_path, 'w', encoding='utf-8') as file:
            print('#############################')
          
            file.write(content)

        print(f"Content written to {full_path}")

def write_data(folder_structure_path):
    converted_data = convert_folder_structure(folder_structure_path)
    boilerplate_path = 'boilerplate.json'
    return write_boilerplate_content(converted_data)