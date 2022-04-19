import json
import unreal
import os
import time


def spawn_actor(path, data):
    actor_class = unreal.EditorAssetLibrary.load_blueprint_class(path)
    actor_location = data['start_location']
    actor_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        actor_location,
        actor_rotation)
    actor.set_editor_property('StartPos', data['start_location'])
    actor.set_editor_property('StartTangent', data['start_tangent'])
    actor.set_editor_property('EndPos', data['end_location'])
    actor.set_editor_property('EndTangent', data['end_tangent'])
    actor.tags = ['newgen']
    return actor


def trace_from_camera():
    start, rotation = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
    end = start + rotation.get_forward_vector() * 10000.0
    _result = unreal.SystemLibrary.line_trace_single(unreal.EditorLevelLibrary.get_editor_world(),
                                                     start, end,
                                                     unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                     True, [], unreal.DrawDebugTrace.NONE, True,
                                                     unreal.LinearColor(1.0, 0.0, 0.0, 1.0),
                                                     unreal.LinearColor(0.0, 1.0, 0.0, 1.0))
    return _result


start_time = time.time()
# paths
gen_actors = []
engine_plugins_dir = unreal.SystemLibrary.convert_to_absolute_path(unreal.Paths.engine_plugins_dir())
roadsys_dir = engine_plugins_dir + 'Runtime/HoudiniEngine/Content/roadSys/'

uasset = '/HoudiniEngine/xPCG_Helper/BP_RoadEdgeDecal_Gen'
exefile = roadsys_dir + 'gen_edge_shapely/gen_edge_shapely.exe'
file_path = roadsys_dir + 'output_cross_splines.json'

if single_mode:
    trace_result = trace_from_camera()
    if trace_result:
        commands = exefile + ' ' + roadsys_dir + ' ' + str(trace_result.to_tuple()[4].x) \
                   + ' ' + str(trace_result.to_tuple()[4].y) + ' ' + str(trace_result.to_tuple()[4].z)
    else:
        commands = ''
else:
    commands = exefile + ' ' + roadsys_dir

if len(commands) > 0:
    unreal.log("commands Begin")
    try:
        os.system(commands)
    except:
        unreal.log_error("Can not run gen_edge_shapely.exe")

    count = 20
    while not os.path.exists(file_path) and count != 0:
        time.sleep(1.0)
        count -= 1

    with open(file_path, 'r') as pf:
        content = json.load(pf)
        if 'spline' in content:
            bplist = content['spline']
            for bp in bplist:
                gen_actors.append(spawn_actor(uasset, bp))

    end_time = time.time() - start_time
    unreal.log("Generation Finished! Processing Time is {:2}s".format(end_time))
    time.sleep(3.0)
    os.remove(file_path)

else:
    unreal.log_error("Too far to find the cross area!")
