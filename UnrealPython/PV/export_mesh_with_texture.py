import unreal
import os
from datetime import date


def get_dependencies_hard(asset_data):
    """ get the dependencies hard from the asset data, deep is one """
    dependencies_hard = None
    if isinstance(asset_data, unreal.AssetData):
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        include_hard_management_references = True
        include_hard_package_references = True
        include_searchable_names = False
        include_soft_management_references = False
        include_soft_package_references = False
        asset_registry_option = unreal.AssetRegistryDependencyOptions(include_hard_management_references,
                                                                      include_hard_package_references,
                                                                      include_searchable_names,
                                                                      include_soft_management_references,
                                                                      include_soft_package_references)

        dependencies_hard = asset_registry.get_dependencies(asset_data.package_name, asset_registry_option)
        #
        # unreal.log("================dependencies_hard===============")
        # for item in dependencies_hard:
        #     unreal.log(item)
    return dependencies_hard


def get_depended_textures(asset_data):
    """ get the depended textures from the asset data, deep is one """
    export_tex = []
    dependencies = get_dependencies_hard(asset_data)
    if not dependencies:
        return None
    for depend in dependencies:  # TODO: to make recursion method
        # get the materials
        if not str(depend).startswith("/Game"):
            continue
        depend_asset = unreal.load_asset(depend)
        depend_asset_data = unreal.EditorAssetLibrary.find_asset_data(depend)
        # get the Textures
        if isinstance(depend_asset, unreal.MaterialInstanceConstant):
            textures = get_dependencies_hard(depend_asset_data)
            for tex in textures:
                if not str(tex).startswith("/Game"):
                    continue
                tex_asset = unreal.load_asset(tex)
                if isinstance(tex_asset, unreal.Texture2D):
                    unreal.log("dependencies texture : %s" % tex_asset.get_name())
                    export_tex.append(tex_asset)
        elif isinstance(depend_asset, unreal.Texture2D):
            export_tex.append(depend_asset)
    return export_tex


def fbx_import_options():
    """ import fbx default options """
    _options = unreal.FbxImportUI()
    _options.import_mesh = True
    _options.import_textures = False
    _options.import_materials = False
    _options.import_as_skeletal = False
    _options.static_mesh_import_data.combine_meshes = True
    _options.static_mesh_import_data.generate_lightmap_uvs = True
    _options.static_mesh_import_data.auto_generate_collision = True
    return _options


def fbx_export_option():
    """ export fbx default options """
    _options = unreal.FbxExportOption()
    _options.ascii = False
    _options.collision = False
    _options.export_local_time = False
    _options.export_morph_targets = True
    _options.export_preview_mesh = True
    _options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2018
    _options.force_front_x_axis = False
    _options.level_of_detail = False
    _options.map_skeletal_motion_to_root = False
    _options.vertex_color = True
    return _options


def create_export_task(exporter, obj, options, name):
    """ create export task and set property """
    _task = unreal.AssetExportTask()
    _task.exporter = exporter
    _task.object = obj
    _task.options = options
    _task.automated = True
    _task.replace_identical = True
    _task.write_empty_files = False
    _task.filename = name
    return _task


def export_folder_check(filename):
    path = os.path.split(filename)[0]
    if not os.path.exists(path):
        os.makedirs(path)


def generate_task_from_asset(asset, folder):
    """ auto generate task by the asset type. only support static mesh, skeleton mesh and 2d texture """
    filename = 'default_export'
    ex = None
    _task = None
    _date = date.today().strftime('%y%m%d')
    if isinstance(asset, unreal.StaticMesh):
        filename = unreal.Paths.project_saved_dir() + 'export/{}/{}/{}.fbx'.format(_date, folder, asset.get_name())
        export_folder_check(filename)
        ex = unreal.StaticMeshExporterFBX()
        _task = create_export_task(ex, asset, fbx_export_option(), filename)
    elif isinstance(asset, unreal.SkeletalMesh):
        filename = unreal.Paths.project_saved_dir() + 'export/{}/{}/{}.fbx'.format(_date, folder, asset.get_name())
        export_folder_check(filename)
        ex = unreal.SkeletalMeshExporterFBX()
        _task = create_export_task(ex, asset, fbx_export_option(), filename)
    elif isinstance(asset, unreal.AnimSequence):
        filename = unreal.Paths.project_saved_dir() + 'export/{}/{}/{}.fbx'.format(_date, folder, asset.get_name())
        export_folder_check(filename)
        ex = unreal.AnimSequenceExporterFBX()
        _task = create_export_task(ex, asset, fbx_export_option(), filename)
    elif isinstance(asset, unreal.Texture2D):
        ex = unreal.TextureExporterTGA()
        filename = unreal.Paths.project_saved_dir() + 'export/{}/{}/{}.tga'.format(_date, folder, asset.get_name())
        export_folder_check(filename)
        _task = create_export_task(ex, asset, None, filename)
    return _task


def make_export_task_list(asset_data):
    # print('make_export_task_list is running')
    _folder = "default_name"
    _tasks = []
    asset = asset_data.get_asset()
    # Mesh :
    if isinstance(asset, unreal.StaticMesh) or isinstance(asset, unreal.SkeletalMesh):
        _folder = asset.get_name()
        _tasks.append(generate_task_from_asset(asset, _folder))
        _depended_textures = get_depended_textures(asset_data)
        unreal.log("_depended_textures num : %s" % len(_depended_textures))
        if _depended_textures:
            for depend in _depended_textures:
                _tasks.append(generate_task_from_asset(depend, _folder))
    # Tex Only:
    elif isinstance(asset, unreal.Texture2D):
        _folder = 'Textures'
        _tasks.append(generate_task_from_asset(asset, _folder))
    # Animation Only:
    elif isinstance(asset, unreal.AnimSequence):
        _folder = 'Animations'
        _tasks.append(generate_task_from_asset(asset, _folder))
    elif isinstance(asset, unreal.MaterialInstanceConstant):
        _folder = asset.get_name()
        _depended_textures = get_depended_textures(asset_data)
        unreal.log("_depended_textures num : %s" % len(_depended_textures))
        if _depended_textures:
            for depend in _depended_textures:
                _tasks.append(generate_task_from_asset(depend, _folder))
    return _tasks


def execute_export_progress():
    unreal.log("============== Export Begin ===============")
    selected_ads = unreal.EditorUtilityLibrary.get_selected_asset_data()
    # get the textures refer to the static mesh
    export_tasks = []
    for asset_data in selected_ads:
        # asset = ad.get_asset()
        ex_tasks = make_export_task_list(asset_data)
        if ex_tasks:
            export_tasks.extend(ex_tasks)
    unreal.log("Export Asset Number: %d"%len(export_tasks))
    # unreal.Exporter.run_asset_export_task(export_tasks[0])
    # begin export tasks, and make a progress dialog
    progress = len(export_tasks)
    current_progress = 0.0
    with unreal.ScopedSlowTask(progress, 'Export Meshes and Textures') as export_task_progress:
        export_task_progress.make_dialog(True)
        for task in export_tasks:
            if export_task_progress.should_cancel():
                # cancel manual
                break
            if task:
                # run export task !
                if unreal.Exporter.run_asset_export_task(task):
                    export_task_progress.enter_progress_frame(1.0, "export : %s success" % (task.object.get_name()))
                else:
                    export_task_progress.enter_progress_frame(1.0, "export : %s failure" % (task.object.get_name()))
            current_progress += 1.0
    # auto open the folder when finished
    path = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + 'export/' + date.today().strftime('%y%m%d')
    os.startfile(path)
    unreal.log("export task finished : %s" % path)
    unreal.log("==============Export End===============")


execute_export_progress()