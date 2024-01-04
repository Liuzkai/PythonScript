import unreal as ue

editor_world = ue.EditorLevelLibrary.get_editor_world()
BP_PV_Root = ue.load_object(None, '/Game/Test/EditorMovies/Tools/PVStageRoot/BP_PV_Root.BP_PV_Root_C')
pv_roots = ue.GameplayStatics.get_all_actors_of_class(editor_world, BP_PV_Root)
if len(pv_roots) > 0:
    pv_root = pv_roots[0]
    levels_to_load = [ue.StringLibrary.conv_name_to_string(tag) for tag in pv_root.tags]
    ue.EditorLevelLibrary.load_level(levels_to_load[0])
    print('Loading ' + levels_to_load[0])
    for sublevel in levels_to_load[1:-1]:
        sublevel_name = sublevel.split('.')[1]
        print('Loading ' + sublevel_name)
        if not ue.NGRPCGLibrary.load_sub_level(sublevel_name):
            print(sublevel_name + ' load failed!')
