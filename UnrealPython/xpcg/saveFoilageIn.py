# Unrealpython/xpcg/saveFoliageIn.py
# by zhongkailiu @20210114
import unreal
import csv


def matrix_to_str(matrix):
    if not isinstance(matrix, unreal.Matrix):
        return "0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0"
    result = str(matrix.x_plane.x) + "," + str(matrix.x_plane.y) + "," + str(matrix.x_plane.z) + "," + str(matrix.x_plane.w) + "," + \
             str(matrix.y_plane.x) + "," + str(matrix.y_plane.y) + "," + str(matrix.y_plane.z) + "," + str(matrix.y_plane.w) + "," + \
             str(matrix.z_plane.x) + "," + str(matrix.z_plane.y) + "," + str(matrix.z_plane.z) + "," + str(matrix.z_plane.w) + "," + \
             str(matrix.w_plane.x) + "," + str(matrix.w_plane.y) + "," + str(matrix.w_plane.z) + "," + str(matrix.w_plane.w)
    return result


a = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                   unreal.InstancedFoliageActor.static_class())
if len(a) > 0:
    # initialize container
    indexTransArray = []
    # get all of foliage data
    for ia in a:
        c = ia.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent.static_class())
        if len(c) == 0:
            continue
        for ic in c:
            count = ic.get_instance_count()
            static_mesh = ic.static_mesh
            index_path = static_mesh.get_path_name()
            index_asset = unreal.EditorAssetLibrary.load_asset(index_path)
            index_bound = index_asset.get_bounding_box()
            index_bound_m = index_bound.max - index_bound.min
            index_height = index_bound_m.z * 0.01
            index_radius = max(index_bound_m.x, index_bound_m.y) * 0.01
            for index in range(0, count):
                index_trans = ic.get_instance_transform(index, world_space=True)
                if index_trans is not None:
                    matrix_data = index_trans.to_matrix()
                    row = index_path + "," + matrix_to_str(matrix_data) + "," + str(index_height) + \
                          "," + str(index_radius)
                    indexTransArray.append(row.split(','))

    # create or open the csv file
    projectPath = unreal.Paths.project_saved_dir()
    filePath = projectPath+"foliageInstance.csv"
    with open(filePath, 'wb') as csvfile:
        w = csv.writer(csvfile)
        w.writerows(indexTransArray)
    csvfile.close()

    outlog = "Export Success, Total Instance :{}".format(len(indexTransArray))
    unreal.log(outlog)