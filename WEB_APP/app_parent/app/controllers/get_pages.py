import os
import json
import zlib
import sys
import base64
def find_extending_files(base_template_name):
    #gets menu.json
    with open("app/controllers/menu.json", 'r') as f:
        menu_data = json.load(f)

    link_to_menu = {}
    for menu_item in menu_data:
        link = menu_item.get("link", None)
        if link:
            link_to_menu[link] = menu_item

        for submenu_item in menu_item.get('submenu', []):
            sub_link = submenu_item.get("link", None)
            if sub_link:
                link_to_menu[sub_link] = submenu_item

    pages = []

    templates_dir = os.path.join(os.getcwd(), "app/templates")

    for filename in os.listdir(templates_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(templates_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            extends_line = "{{% extends \"{}\" %}}".format(base_template_name)
            if extends_line in content:  # Indentation corrected here
                compressed_content = zlib.compress(content.encode('utf-8'))
                compressed_content_str = base64.b64encode(compressed_content).decode('utf-8')
                link = filename.replace(".html", "")
                name = link
                parent_menu = None
                menu_item = link_to_menu.get(link, {})
                if menu_item:
                    name = menu_item.get('name', name)
                    parent_menu = menu_item.get('parent_menu', parent_menu)

                
                pages.append({
                    "link": link,
                    "name": name,
                    "content": compressed_content_str,  # Store the base64-encoded string
                    "parent_menu": parent_menu
                })

    return pages  


# Example usage
result = find_extending_files