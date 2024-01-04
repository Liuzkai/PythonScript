import unreal as ue

# check if loaded sequence is exist
loaded_level_seq = ue.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
if loaded_level_seq is not None:
    print('Current Level Sequence:', loaded_level_seq)
    # check if BP_PV_Root is exist
    editor_world = ue.EditorLevelLibrary.get_editor_world()
    BP_PV_Root = ue.load_object(None, '/Game/Test/EditorMovies/Tools/PVStageRoot/BP_PV_Root.BP_PV_Root_C')
    pv_roots = ue.GameplayStatics.get_all_actors_of_class(editor_world, BP_PV_Root)
    pv_root = pv_roots[0] if len(pv_roots) > 0 else None

    if pv_root is None:
        print('Could not find, Create a new PV Root')
        #new create pv_root
        cam_loc, cam_rot = ue.EditorLevelLibrary.get_level_viewport_camera_info()
        cam_loc += cam_rot.get_forward_vector() * 100.0
        pv_root = ue.EditorLevelLibrary.spawn_actor_from_class(BP_PV_Root, cam_loc, cam_rot)
        # add pv_root to sequence

    # get levels path
    loaded_levels = ue.NGRPCGLibrary.get_all_loaded_sub_level()
    levels_path_name = ue.Array(ue.Name)
    for level in loaded_levels:
        levels_path_name.append(level.get_path_name().split(':')[0])
        # levels_path_name.append(level.get_path_name().rstrip(':PersistentLevel'))
        # levels_path_name.append(level.get_path_name())

    # with ue.ScopedEditorTransaction('PVUpdateSequenceLevelTags') as trans:
    ue.SystemLibrary.begin_transaction('PVUpdateSequenceLevelTags','PVUpdateSequenceLevelTags', None)
    pv_root.actor_remove_all_tags()
    pv_root.set_editor_property('tags', levels_path_name)
    ue.SystemLibrary.end_transaction()
    print('Finished PV Update Sequence Level Tags')
else:
    print('No Level Sequence Exist!')