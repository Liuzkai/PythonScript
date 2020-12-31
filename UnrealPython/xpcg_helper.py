import unreal

def get_landscape_bounds():
    landscape = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                                     unreal.Landscape)
    landscape_proxy = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                                   unreal.LandscapeProxy)
    processing_landscape = None
    if landscape_proxy is None :
        processing_landscape = landscape
    else :
        processing_landscape = landscape_proxy
    unreal.EditorLevelLibrary.set_selected_level_actors(processing_landscape)
    bounds = unreal.EditorUtilityLibrary.get_selection_bounds()
    unreal.log(" get the landscape origianl : %s  and extent : %s" % (bounds[0].to))
    return bounds


def make_capture(render_target, location):
    capture_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D,location)
    return capture_actor


     
location = get_landscape_bounds()[0]
render_target = unreal.RenderingLibrary.create_render_target2d(None,4096,4096,unreal.TextureRenderTargetFormat.RTF_RGBA8)
capture = make_capture(render_target, location)
unreal.log(capture)
