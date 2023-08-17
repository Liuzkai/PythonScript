import unreal as ue

if __name__ == "__main__":
    actors = ue.EditorLevelLibrary.get_selected_level_actors()
    root_class = ue.EditorAssetLibrary.load_blueprint_class("/Game/Test/EditorMovies/Tools/PVStageRoot/BP_PVStageRoot")
    actor_trans_array = []
    root = None
    for actor in actors:
        if actor.get_class() == root_class:
            root = actor
        else:
            actor_trans_array.append(actor)
    center = ue.GameplayStatics.get_actor_array_average_location(actor_trans_array)
    # for actor in actors:
    #     actor_loc = actor.get_actor_location()
    #     actor.set_actor_location(actor_loc - center, False, False)
    root_trans = root.get_actor_location()
    root.set_actor_location(center - root_transae, False, False)
    ue.log(center)

    # ue.log(seq)
    # for track in tracks:
    #     ue.log(track)