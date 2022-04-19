import unreal

actors = unreal.GameplayStatics.get_all_actors_with_tag(unreal.EditorLevelLibrary.get_editor_world(),
                                                        unreal.Name('roadsys_decal'))
count = 0
for actor in actors:
    comp = actor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    level = actor.get_outer()
    unreal.EditorLevelLibrary.set_current_level_by_name(level.get_path_name().split('.')[-1].split(':')[0])
    levelStreaming = unreal.GameplayStatics.get_streaming_level(unreal.EditorLevelLibrary.get_editor_world(),
                                                                level.get_full_name().split(":")[0])
    unreal.log(level.get_full_name())
    unreal.log(levelStreaming)
    static_mesh = comp.static_mesh
    instance_num = comp.get_instance_count()
    create_list = []
    for i in range(instance_num):
        trans = comp.get_instance_transform(i, True)
        new_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, trans.translation)
        new_actor.set_actor_label('xPCG_Roadsys_decals_{}'.format(count))
        new_actor.static_mesh_component.set_static_mesh(static_mesh)
        new_actor.set_actor_transform(trans, False, False)
        new_actor.tags = ['roadsys', 'roadsys_decal', static_mesh.get_name()]
        create_list.append(new_actor)
        count += 1
    # delete bp
    unreal.EditorLevelLibrary.destroy_actor(actor)

