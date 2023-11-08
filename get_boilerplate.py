import json
import base64
import zlib

def encode_to_base64(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        print(file_content)
        encoded_content = base64.b64encode(file_content.encode('utf-8'))

        return encoded_content.decode('utf-8')
    except FileNotFoundError:
        raise FileNotFoundError("The file was not found at the specified path.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def compress_base64(base64_string):
    try:
        bytes_to_compress = base64_string.encode('utf-8')
        compressed_data = zlib.compress(bytes_to_compress)

        return compressed_data
    except Exception as e:
        raise Exception(f"An error occurred during compression: {e}")

def compress_boilerplate():
    with open('./boilerplate.json','r') as hg:
        boilerplate_json=json.loads(hg.read())
    for name in [obj.get('name') for obj in boilerplate_json]:
        indexed_current_object = ((index, item) for index, item in enumerate(boilerplate_json) if item.get('name') == name)
        current_object_path = (f'boilerplate/{(next(indexed_current_object)[1])["name"]}.txt')
        print(current_object_path)
        try:
            print('trying')
            current_obj_b64 = encode_to_base64(current_object_path)
            print('converted to base64')
            try:
                print('about to compress')
                current_obj_b64_zlib = compress_base64(current_obj_b64)
                (boilerplate_json[(int(next(indexed_current_object)[0]))])['content']=current_obj_b64_zlib
                print('##########')
                print('COMPRESSED')
                print('##########')
                print(current_obj_b64_zlib)

            except:
                print('##########')
                print("ZLIB ERROR")
                print('##########')
                continue

        except:
            print('error')
            continue

    return boilerplate_json

def write_boilerplate_content():
    with open('boilerplate.json') as h:
        prepared_json = json.dumps(compress_boilerplate())
        print(prepared_json)
        h.write(prepared_json)