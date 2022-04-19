import unreal
import time


def set_comp_mobility(Comp, Cull):
        # unreal.log("setCompMobility() : " + Comp.static_mesh.get_name())
        current_actor = unreal.EditorLevelLibrary.get_selected_level_actors()[0]
        comps = current_actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for c in comps:
            if c.static_mesh.get_name() == Comp.static_mesh.get_name():
                c.set_cull_distances(Cull[0], Cull[1])
                c.set_collision_profile_name("NoCollision")
                c.set_editor_property('mobility', unreal.ComponentMobility.STATIC)


def set_decal_properties(Comp, Cull, inVirtualTexture=None, sort=90):
    # unreal.log("setDecalProperties() : " + Comp.static_mesh.get_name())
    current_actor = unreal.EditorLevelLibrary.get_selected_level_actors()[0]
    comps = current_actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
    for c in comps:
        if c.static_mesh.get_name() == Comp.static_mesh.get_name():
            c.set_editor_property('mobility', unreal.ComponentMobility.STATIC)

    current_actor = unreal.EditorLevelLibrary.get_selected_level_actors()[0]
    comps = current_actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
    for c in comps:
        if c.static_mesh.get_name() == Comp.static_mesh.get_name():
            c.set_editor_property('translucency_sort_priority', sort)

    current_actor = unreal.EditorLevelLibrary.get_selected_level_actors()[0]
    comps = current_actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
    for c in comps:
        if c.static_mesh.get_name() == Comp.static_mesh.get_name():
            c.set_collision_profile_name("NoCollision")
            c.set_cull_distances(Cull[0], Cull[1])
            c.set_editor_property('runtime_virtual_textures', inVirtualTexture)

    # Comp.set_cull_distances(505.0, 1100.0)
    # set tag


def get_the_foliage(content):
    result = []
    for col in content:
        if col != "":
            col_elems = col[2:-2]
            col_list = col_elems.split('),(')
            for lis in col_list:
                result.append(lis.split('\"\',bound')[0].split('.')[-1])
    return result


def get_decal_name_and_sort(datatable):
    roadSysDecalsTable = datatable
    if datatable is None:
        roadSysDecalsTable = unreal.EditorAssetLibrary.load_asset('/HoudiniEngine/xPCG_Helper/Data/DT_RoadsysDecals')

    if isinstance(roadSysDecalsTable, unreal.DataTable):
        decalMeshColumns = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(roadSysDecalsTable, "DecalMesh")
        sortColumns = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(roadSysDecalsTable, "Sort")
        FoliageColumns = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(roadSysDecalsTable, "GenFoliage")
        return [col.split('.')[-1][:-1] for col in decalMeshColumns], [int(sort) for sort in sortColumns], get_the_foliage(FoliageColumns)


def processing(start, end):
    unreal.log("blueprint processing!")

    Cull = (start, end)
    # get targets
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    bp = actors[0] if len(actors) > 0 else None

    assets = unreal.EditorUtilityLibrary.get_selected_assets()
    dt = None
    if len(assets) > 0:
        if isinstance(assets[0], unreal.DataTable):
            dt = assets[0]

    # get dt decal info and sort
    decalFilter, decalSort, foliageFilter = get_decal_name_and_sort(dt)

    # get virtual texture
    virtualTextureVolumes = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                                    unreal.RuntimeVirtualTextureVolume)
    virtualTexture = [vt.virtual_texture_component.virtual_texture for vt in virtualTextureVolumes]

    # processing main

    if bp is not None :
        if "xPCG_roadsys" in bp.get_actor_label() or 'xPCG_Roadsys' in bp.get_actor_label() :
            instance_comps = bp.get_components_by_class(unreal.InstancedStaticMeshComponent)
            count = 0
            target = len(instance_comps)
            success = True
            if instance_comps:
                with unreal.ScopedSlowTask(target, 'Processing Blueprint ...') as slow_task:
                    slow_task.make_dialog(True)
                    for comp in instance_comps:

                        if slow_task.should_cancel():
                            break

                        decal_mesh_name = comp.static_mesh.get_name()

                        if decal_mesh_name in decalFilter:
                            index = decalFilter.index(decal_mesh_name)
                            decal_sort = decalSort[index] if index >= 0 else 0
                            set_decal_properties(comp, Cull, virtualTexture, decal_sort)
                        elif decal_mesh_name in foliageFilter:
                            set_comp_mobility(comp, Cull)
                        else:
                            unreal.log_warning(" There is not a " + decal_mesh_name + " in the data table !!!")
                            success = False

                        count += 1
                        success_status = " successfully !" if success else "failed !"
                        message = "Processing " + decal_mesh_name + success_status + "    " + str(count) + '/' + str(target)
                        slow_task.enter_progress_frame(1, message)
                        if not success:
                            time.sleep(1.0)


# Main
# instart, inend from blueprint
processing(instart, inend)