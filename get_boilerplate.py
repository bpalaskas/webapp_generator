import json
import base64
import zlib

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