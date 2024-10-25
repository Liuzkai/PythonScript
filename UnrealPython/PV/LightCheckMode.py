import unreal as ue

# Was ppv existed ?
AllActors = ue.EditorLevelLibrary.get_all_level_actors()
ppv_class = ue.PostProcessVolume
AllPPV = ue.GameplayStatics.get_all_actors_of_class(ue.EditorLevelLibrary.get_editor_world(), ppv_class)
# AllPPV = ue.EditorFilterLibrary.by_class(AllActors, ppv_class)
check_bp = ue.load_object(None, '/Game/Test/EditorMovies/Tools/PVHelper/Toolset/BP_LightingChecker')
AllCheck = ue.EditorFilterLibrary.by_actor_tag(AllActors, u'LightingCheckMode')
# print(u'ALl PPV Num is ' + str(len(AllPPV)))
if len(AllCheck) == 0:
    # No PPV found
    print("Lighting Check Mode On")
    actor_location, actor_rot = ue.EditorLevelLibrary.get_level_viewport_camera_info()
    ppv = ue.EditorLevelLibrary.spawn_actor_from_object(check_bp, actor_location, actor_rot, False)
    # set ppv priority
    max_priority = 0.0
    for other_ppv in AllPPV:
        priority = other_ppv.priority
        if priority > max_priority:
            max_priority = priority
    # ppv.ppv_priority = max_priority + 1.0
    # print("Max priority is", max_priority)
    ppv.set_editor_property('ppv_priority', (max_priority + 1.0))
    # set ppv tags
    ppv.actor_add_tag(u'LightingCheckMode')

else:
    print("Lighting Check Mode Off")
    for bp_ppv in AllCheck:
        ue.EditorLevelLibrary.destroy_actor(bp_ppv)