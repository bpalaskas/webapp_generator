import os
from make_boilerplate import return_file_contents
from init import new_site_dir, structure_path
from functools import lru_cache
import bs4 
import json
import re
templates = []
formatted_settings_list=[]
formatted_settings=[]
def get_single_template(name):
    for template in templates:
        if template['name'] == name:
            return {"template":template,"index":templates.index(template)}
def get_placeholder_value(placeholder):
    for item in formatted_settings:
        if item['template_name'] == placeholder:
            return item['value']
with open('boilerplate.json', 'r') as blp:
    BOILERPLATE =json.load(blp)
@lru_cache   
def get_settings():
    with open('user_input_templates/settings.json', 'r') as json_settings:
        SETTINGS =json.load(json_settings)
    return SETTINGS
def format_settings(entries):
    entries=entries['website']
    for entry in entries:
        if type(entries[entry])==str:
            formatted_settings.append({'name':entry,"value":entries[entry],"template_name":f'***{entry}***'})
        else:
            for val in (entries[entry]):
                for subval in ((entries[entry])[val]):
                    print("ENTRIES")
                    print(entries)
                    print('ENTRY')
                    print(entries[entry])
                    print('ENTRY-VAL')
                    print((entries[entry])[val])
                    print("SUBVAL")
                    print(subval)
                    if not isinstance(subval, dict):
                        print(val)
                        try:
                            if entry[val]==list(entry)[-1]
                            formatted_settings.append({"parent_name":entry,"name":entry[val],"value":subval,"template_name":f'***{entry}:{val}:{subval}***'})
                        except:
                            formatted_settings.append({"parent_name":entry,"name":val,"value":subval,"template_name":f'***{entry}:{val}:{subval}***'})

                    else:
                        for att_key, att_val in (((entries[entry])[val])[subval]):
                            formatted_settings.append({"parent_name":key, "name":subkey,"value":(((entries[entry])[val])[subval])[att_key],"template_name":f'{val}:{subval}:{att_key}'})
    formatted_settings_json=json.dumps(formatted_settings)
    with open('formatted_settings.json','w') as fs:
        fs.write(formatted_settings_json)
    formatted_settings_list=formatted_settings
    return formatted_settings

def get_placeholders(content):
    result = re.findall(r'(\*\*\*\w+\*\*\*)', content)
    return result
def get_templates():
    for file in BOILERPLATE:
        if ('.html' in file['path'])==True:
            templates.append({"name":file['name'],"content":file["content"]})    
def inject(template):
    _template=template['template']
    _content=_template['content']
    current_placeholders=get_placeholders(_content)
    for ph in current_placeholders:
        ph_value = get_placeholder_value(ph)
        
        if ph_value != None:
            _template['content']=(_template['content']).replace(ph, ph_value)
        else:
            continue
    return  {"template": _template,"index":template['index']}
################################
#TESTING#
#SHOULD BE REPLACED WITH CLI SEQUENCE WHERE USER CAN DECIDE PATH TO CREATE WEB APP#
################################
format_settings(get_settings())
get_templates()
with open('boilerplate.json') as bp:
    bp_json=json.load(bp)
for template in templates:
    for obj in bp_json:
        if (template['name']) == obj['name']:
            _template=(inject(get_single_template(template['name'])))
            obj['content']=_template['template']['content']
new_bp_json=json.dumps(bp_json)
with open('boilerplate.json', "w") as new_bp:
    new_bp.write(new_bp_json)
    