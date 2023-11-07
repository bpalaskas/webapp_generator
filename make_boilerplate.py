import json
import os

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
def write_data(folder_structure_path):
    converted_data = convert_folder_structure(folder_structure_path)
    boilerplate_path = 'boilerplate.json'

    with open(boilerplate_path, 'w') as bp_file:
        json.dump(converted_data, bp_file, indent=4)
