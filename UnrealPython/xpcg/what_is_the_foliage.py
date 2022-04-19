import unreal


start, rotation = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
end = start + rotation.get_forward_vector() * 10000.0
actors = unreal.EditorLevelLibrary.get_all_level_actors()
# print actors[0]
# actors_except_foliage = unreal.EditorLevelLibrary.get_selected_level_actors()
# print actors_except_foliage[0]

result = unreal.SystemLibrary.box_trace_single(unreal.EditorLevelLibrary.get_editor_world(),
                                               start, end, unreal.Vector(300.0, 300.0, 300.0), rotation,
                                               unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                               True, [], unreal.DrawDebugTrace.NONE, True,
                                               unreal.LinearColor(1.0, 0.0, 0.0, 1.0),
                                               unreal.LinearColor(0.0, 1.0, 0.0, 1.0))


if result:
    hit_component = result.to_tuple()[10]
    print hit_component
    if isinstance(hit_component, unreal.FoliageInstancedStaticMeshComponent):
        asset_path = hit_component.static_mesh.get_path_name()
        unreal.EditorAssetLibrary.sync_browser_to_objects([asset_path])