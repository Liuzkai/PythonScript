import unreal


def trace_screen():
    start, rotation = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
    end = start + rotation.get_forward_vector() * 10000.0
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

    result = unreal.SystemLibrary.line_trace_single(unreal.EditorLevelLibrary.get_editor_world(),
                                                   start, end,
                                                   unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                   True, [], unreal.DrawDebugTrace.FOR_DURATION, True,
                                                   unreal.LinearColor(1.0, 0.0, 0.0, 1.0),
                                                   unreal.LinearColor(0.0, 1.0, 0.0, 1.0))
    return result


def spawnActor(path, location):
    actor_class = unreal.EditorAssetLibrary.load_blueprint_class(path)
    actor_location = location
    actor_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        actor_location,
        actor_rotation)


result = trace_screen()
if result:
    loc = result.to_tuple()[5]
    path = '/HoudiniEngine/xPCG_Helper/BP_RoadEdgeDecal'
    spawnActor(path, loc)
    unreal.log('Gen Road Edge Decal Successfully!')
else:
    unreal.log_warning('No Location Found for Generation!')