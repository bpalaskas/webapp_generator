import os
import json
import make_boilerplate
def load_structure_from_json(json_path):
    with open(json_path, 'r') as json_file:
        return json.load(json_file)
def create_file(file_path):
    with open(file_path, 'x') as f:
        pass  
def create_structure(base_path, structure):
    for name, content in structure.items():
        if isinstance(content, dict):
            folder_path = os.path.join(base_path, name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Create files if 'files' key is present
            if 'files' in content:
                for file_name in content['files']:
                    file_path = os.path.join(folder_path, file_name)
                    if not os.path.exists(file_path):  # Check if file already exists before creating
                        create_file(file_path)

            # Recursively process any nested directories
            for key, value in content.items():
                if isinstance(value, dict):
                    nested_folder_path = os.path.join(folder_path, key)
                    create_structure(nested_folder_path, value)
new_site_dir = './WEB_APP2'
structure_path = './structure.json'

# Starting point of the script, NEEDS to be nothing but a sequence of functions in ordder, that will never change
if __name__ == '__main__':
    new_site_dir = './WEB_APP2'
    base_path = os.path.join(os.getcwd(), new_site_dir)

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    structure_path = './structure.json'
    flask_app_structure = load_structure_from_json(structure_path)

    create_structure(base_path, flask_app_structure)
    make_boilerplate.write_contents_to_files((make_boilerplate.write_data(structure_path)),new_site_dir)
    print(f"Flask project structure created at {base_path}")