import unreal


unreal.EditorLoadingAndSavingUtils.export_scene(export_selected_actors_only=True)

# coding: utf-8



def fbx_static_mesh_import_data():
    _static_mesh_import_data = unreal.FbxStaticMeshImportData()
    _static_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    _static_mesh_import_data.import_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    _static_mesh_import_data.import_uniform_scale = 1.0
    _static_mesh_import_data.combine_meshes = True
    _static_mesh_import_data.generate_lightmap_u_vs = True
    _static_mesh_import_data.auto_generate_collision = True
    return _static_mesh_import_data


def fbx_skeletal_mesh_import_data():
    _skeletal_mesh_import_data = unreal.FbxSkeletalMeshImportData()
    _skeletal_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    _skeletal_mesh_import_data.import_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    _skeletal_mesh_import_data.import_uniform_scale = 1.0
    _skeletal_mesh_import_data.import_morph_targets = True
    _skeletal_mesh_import_data.update_skeleton_reference_pose = False
    return _skeletal_mesh_import_data


def fbx_import_option(static_mesh_import_data = None, skeletal_mesh_import_data = None):
    _options = unreal.FbxImportUI()
    _options.import_mesh = True
    _options.import_textures = False
    _options.import_materials = False
    _options.import_as_skeletal = False
    _options.static_mesh_import_data = static_mesh_import_data
    _options.skeletal_mesh_import_data = skeletal_mesh_import_data
    return _options


def create_import_task(file_name, destinataion_path, options=None):
    _task = unreal.AssetImportTask()
    _task.automated = True
    _task.destination_path = destinataion_path
    _task.filename = file_name
    _task.replace_existing = True
    _task.save = True
    _task.options = options
    return _task


def executeImportTasks(tasks):
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for task in tasks:
        for path in task.get_editor_property('imported_object_paths'):
            print('Improted: %s' % path)


def importMyAssets():
    static_mesh_task = buildImportTask(
        static_mesh_fbx, '/Game/Temp/StaticMeshes', buildStaticMeshImportOptions())
    skeletal_mesh_task = buildImportTask(
        skeletal_mesh_fbx, '/Game/Temp/SkeletalMeshes', buildSkeletalMeshImportantOptions())
    executeImportTasks([static_mesh_task, skeletal_mesh_task])


# target fbx
static_mesh_fbx = 'C:/sm_box.fbx'
skeletal_mesh_fbx = 'C:/sk_character.fbx'
# set the input option
import_static_mesh_option = fbx_import_option(static_mesh_import_data=fbx_static_mesh_import_data())
import_skeletal_mesh_option = fbx_import_option(skeletal_mesh_import_data=fbx_skeletal_mesh_import_data())
# generate task
import_static_mesh_task = create_import_task(static_mesh_fbx, '/Game/StaticMesh/', import_static_mesh_option)
import_skeletal_mesh_task = create_import_task(static_mesh_fbx, '/Game/SkeletalMesh/', import_skeletal_mesh_option)
total_task = [import_static_mesh_task, import_skeletal_mesh_task]
# run the task
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(total_task)