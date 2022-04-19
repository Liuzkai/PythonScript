import unreal
import csv


def get_static_mesh_data(asset):
    if isinstance(asset, unreal.StaticMesh):
        name = asset.get_name()
        path = "StaticMesh\'" + asset.get_path_name() + "\'"
        bound = asset.get_bounding_box()
        box = bound.max - bound.min
        height = max( box.z / 100.0, 0.01 )
        radius = max( max(box.x, box.y) / 100.0, 0.01)
        return name, path, radius, height
    return None, None, None, None


def write_to_csv(data, path, write_mode):
    if len(data) == 0 :
        unreal.log_warning("The data is empty!")
        return False

    if not path.endswith('/') and not path.endswith('\\'):
        unreal.log_warning("add / at end")
        path += '/'

    file_path = path + 'foliage.csv'

    mode = "wb+" if write_mode == 'Replace' else "ab+"

    with open(file_path, mode) as f:
        writer = csv.writer(f)
        writer.writerow(["name", "path", "radius", "height"])
        writer.writerows(data)
        f.close()
    return True


def fill_data_list(asset, data, name):
    if isinstance(asset, unreal.FoliageType):
        f_path = "FoliageType_InstancedStaticMesh\'" + asset.get_path_name() + "\'"
        sm_asset = asset.get_editor_property('mesh')
        f_name, _, f_radius, f_height = get_static_mesh_data(sm_asset)
        if f_name is not None:
            data.append((f_name, f_path, f_radius, f_height))
            name.append(f_name)
    elif isinstance(asset, unreal.StaticMesh):
        s_name, s_path, s_radius, s_height = get_static_mesh_data(asset)
        if s_name not in name and s_name is not None:
            data.append((s_name, s_path, s_radius, s_height))
            name.append(s_name)


assets = unreal.EditorUtilityLibrary.get_selected_assets()
data = []
name = []
for asset in assets:
    if isinstance(asset, unreal.DataTable):
        columns = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(asset, unreal.Name("Foliage"))
        for column in columns:
            if column is "None":
                continue
            c_asset = unreal.load_asset(column)
            fill_data_list(c_asset, data, name)
    else:
        fill_data_list(asset, data, name)

# input parameters: filepath, write_m
if write_to_csv(data, filepath, write_m) :
    output_log = "Export Foliage Number : " + str(len(data)) + "\nFile Path: " + filepath + 'foliage.csv'
    unreal.log(output_log)
else:
    unreal.log_warning("write to csv fail!")