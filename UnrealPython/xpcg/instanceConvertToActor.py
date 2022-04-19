import unreal

actors = unreal.EditorLevelLibrary.get_selected_level_actors()
count = 0

def add_unique(e, array):
    if len(array) == 0:
        array.append(e)
        return
    found = False
    for a in array:
        if a.equals(e):
            found = True
            break

    if not found:
        array.append(e)
        # unreal.log("x {}, y {}, z {}".format(e.translation.x, e.translation.y, e.translation.z))


for actor in actors:
    level = actor.get_outer()
    unreal.EditorLevelLibrary.set_current_level_by_name(level.get_path_name().split('.')[-1].split(':')[0])
    levelStreaming = unreal.GameplayStatics.get_streaming_level(unreal.EditorLevelLibrary.get_editor_world(),
                                                                level.get_full_name().split(":")[0])

    components = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    if components is None:
        components = actor.get_components_by_class(unreal.InstancedStaticMeshComponent)

    if components is not None:
        for comp in components:
            trans_array = []

            static_mesh = comp.static_mesh
            instance_num = comp.get_instance_count()
            for i in range(instance_num):
                trans = comp.get_instance_transform(i, True)
                add_unique(trans, trans_array)

            if trans_array:
                for trans in trans_array:
                    new_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,
                                                                                 trans.translation)
                    new_actor.static_mesh_component.set_static_mesh(static_mesh)
                    new_actor.set_actor_label("{}_{}".format(static_mesh.get_name(), count))
                    new_actor.set_actor_transform(trans, False, False)
                    count += 1



