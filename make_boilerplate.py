import json
import os
import base64

def return_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        raise FileNotFoundError("The file was not found at the specified path.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def compress_boilerplate(data):
    boilerplate_json = data
    for obj in boilerplate_json:
        name = obj.get('name')
        if name:
            # Find the index of the current object with matching name
            index = next((i for i, item in enumerate(boilerplate_json) if item.get('name') == name), None)
            if index is not None:
                current_object_path = f'boilerplate/{name}.txt'
                print(current_object_path)
                try:
                    current_obj_content = return_file_contents(current_object_path)
                    print('file contents retrieved')
                    # Update the content of the object at the found index
                    boilerplate_json[index]['content'] = current_obj_content
                    print("success")
                except Exception as e:
                    print('##########')
                    print(f"Error while updating object with name {name}: {e}")
                    print('##########')
            else:
                print(f'No object with name {name} found.')
    return boilerplate_json

def write_boilerplate_content(boilerplate_data):
    prepared_json = compress_boilerplate(boilerplate_data)
    return prepared_json

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