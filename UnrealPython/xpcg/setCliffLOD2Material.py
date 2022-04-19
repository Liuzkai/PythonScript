# -*- coding: UTF-8 -*-

import unreal

# 请替换材质路径
material_path = '/Game/ArkGame/Environment/Houdini_Asset/cliffSys/M_cliff_Inst1'


def set_cliff_mat(static_mesh, LODs, screen_size_array):
    # set lod section material
    if static_mesh is not None:
        if 'cliffSys' in static_mesh.get_name() and isinstance(static_mesh, unreal.StaticMesh):
            # static_mesh.set_editor_property("bAutoComputeLODScreenSize", 0)
            # default to use the second material slot
            # asset_path = static_mesh.get_path_name()
            for level in LODs:
                unreal.EditorStaticMeshLibrary.set_lod_material_slot(static_mesh, 1, level, 0)
            #  set lod screen size
            # unreal.log(static_mesh)
            # static_mesh = unreal.load_asset(asset_path)
            # unreal.log(static_mesh)
            unreal.EditorStaticMeshLibrary.set_lod_screen_sizes(static_mesh, screen_size_array)


def add_cliff_mat(static_mesh, LODs, mat, screen_size_array):
    # get materials
    if not mat:
        unreal.log_error("material is invalid!")
        return
    if not static_mesh:
        unreal.log_error("static mesh is invalid!")
        return

    # set lod section material
    if static_mesh is not None and mat is not None:
        if 'cliffSys' in static_mesh.get_name() and isinstance(static_mesh, unreal.StaticMesh):
            # static_mesh.set_editor_property("bAutoComputeLODScreenSize", 0)
            new_material = static_mesh.add_material(mat)
            slot_num = static_mesh.get_material_index(new_material)
            for level in LODs:
                unreal.EditorStaticMeshLibrary.set_lod_material_slot(static_mesh, slot_num, level, 0)
            #  set lod screen size
            unreal.EditorStaticMeshLibrary.set_lod_screen_sizes(static_mesh, screen_size_array)


def get_static_mesh_filter_by_name(actors, name):
    if len(actors) == 0:
        return None
    static_mesh_array = []
    for actor in actors:
        if isinstance(actor, unreal.StaticMeshActor) and actor is not None and name in actor.get_actor_label():
            actor.tags = [unreal.Name('cliffsys')]
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            static_mesh = comp.static_mesh
            if static_mesh is not None:
                asset_path = static_mesh.get_path_name()
                static_mesh_asset = unreal.load_asset(asset_path)
                static_mesh_array.append(static_mesh_asset)
    return static_mesh_array


def run(LODs, add, mat, screen_sizes):

    # actors = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
    #                                                         unreal.StaticMeshActor)
    # static_mesh_array = get_static_mesh_filter_by_name(actors, 'xPCG_Cliffsys')
    # actors = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
    #                                                         unreal.StaticMeshActor)
    # static_mesh_array = get_static_mesh_filter_by_name(actors, 'xPCG_Cliffsys')
    # unreal.EditorAssetLibrary.
    static_mesh_array = unreal.EditorUtilityLibrary.get_selected_assets()
    # unreal.log("start")
    # unreal.log(len(static_mesh_array_A))
    # for A in static_mesh_array_A:
    #     for s in static_mesh_array:
    #         if s == A:
    #             unreal.log(s)

    # unreal.log(static_mesh_array[0])

    if add is False:
        for static_mesh in static_mesh_array:
            # unreal.log(static_mesh)
            set_cliff_mat(static_mesh, LODs, screen_sizes)
    else:
        for static_mesh in static_mesh_array:
            add_cliff_mat(static_mesh, LODs, mat, screen_sizes)
    # unreal.log(" finished! ")
    # assets = unreal.EditorAssetLibrary.save_loaded_assets(static_mesh_array, True)



# LOD = cliff_lod
# import sys
# sys.path.append("D:\\UGit\\Unrealpython\\xpcg\\")
# import setCliffLOD2Material as ct
# reload(ct)
run(cliff_lod, add, material, screen_sizes)

# run(cliff_lod, add, material)

# select_assets = unreal.EditorUtilityLibrary.get_selected_assets()
#
# select_assets[0].set_editor_property("bAutoComputeLODScreenSize", 0)