import unreal
import os


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
    _options.export_local_time = True
    _options.export_morph_targets = False
    _options.export_preview_mesh = False
    _options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2013
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


def generate_task_from_asset(asset, name):
    """ auto generate task by the asset type. only support static mesh and 2d texture """
    filename = unreal.Paths.project_saved_dir() + 'export/' + name + '/' + asset.get_name() + '.fbx'
    ex = None
    _task = None
    if isinstance(asset, unreal.StaticMesh):
        ex = unreal.StaticMeshExporterFBX()
        _task = create_export_task(ex, asset, fbx_export_option(), filename)
    elif isinstance(asset, unreal.Texture2D):
        ex = unreal.TextureExporterTGA()
        filename = unreal.Paths.project_saved_dir() + 'export/' + name + '/' + asset.get_name() + '.tga'
        _task = create_export_task(ex, asset, None, filename)
    return _task


# AssetToolsHelpers High Level Method ( The dialog windows can not avoid appeared)
# export = unreal.AssetToolsHelpers.get_asset_tools().export_assets_with_dialog([asset_sld[0].get_path_name()], False)
# export = unreal.AssetToolsHelpers.get_asset_tools().export_assets([asset_sld[0].get_path_name()], filename)
unreal.log("==============Export Begin===============")
# ======================================================================== #
assets = unreal.EditorUtilityLibrary.get_selected_asset_data()
# get the textures refer to the static mesh
export_asset = []
file_name = "default_object"
for asset_data in assets:
    # only export mesh ?
    if isinstance(asset_data.get_asset(), unreal.StaticMesh):
        file_name = asset_data.get_asset().get_name()
        unreal.log("export asset : %s" % file_name)
        export_asset.append(asset_data.get_asset())
    dependencies = get_dependencies_hard(asset_data)
    for depend in dependencies:
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
                    unreal.log("export asset : %s" % tex_asset.get_name())
                    export_asset.append(tex_asset)


unreal.log("Export Asset Number: %d"%(len(export_asset)))
file_name = 'default_name'
export_tasks_sm = []
export_tasks_tx = []
# generate the export tasks
for t in export_asset:
    if isinstance(t, unreal.StaticMesh):
        file_name = t.get_name()
        export_tasks_sm.append(generate_task_from_asset(t, file_name))
    else:
        export_tasks_tx.append(generate_task_from_asset(t, file_name))

# export texture first, because it will fail if export fbx when the folder do not exist
export_tasks = export_tasks_tx + export_tasks_sm
for task in export_tasks:
    unreal.log(task.object.get_name())
# begin export tasks, and make a progress dialog
progress = len(export_tasks)
current_progress = 1.0
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
path = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + 'export/'
os.startfile(path)
unreal.log("export task finished : %s" % path)
unreal.log(unreal.Paths.project_saved_dir())
unreal.log("==============Export End===============")