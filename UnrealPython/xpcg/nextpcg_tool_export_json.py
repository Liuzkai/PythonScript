'''
export spline type to json file.
'''
import unreal
import json
import os

unreal.log(type(terrain_type_array))
type_array = list(terrain_type_array)
relpath = unreal.Paths.project_saved_dir()
path = unreal.Paths.convert_relative_path_to_full(relpath)
jsonfile = path + 'nextpcg_terrain_curve_type.json'
content = {"type": type_array}
with open(jsonfile, 'w') as Jn:
    json.dump(content, Jn)
    Jn.close()
json_path = 'failed!'
if os.path.exists(jsonfile):
    json_path = jsonfile

