import unreal


class myBound():

    def __init__(self, bound):
        self.bound = bound
        self.level = bound.get_outer()
        self.bounds = bound.get_actor_bounds(False)  # (origin, box_extent)
        self.name = self.level.get_path_name().split('.')[-1].split(':')[0]

    def __eq__(self, other):
        return self.is_in_bound(other)

    def is_in_bound(self, actor):
        loc = actor.get_actor_location()
        origin = self.bounds[0]
        extent = self.bounds[1]
        if abs(loc.x - origin.x) <= extent.x and abs(loc.y - origin.y) <= extent.y:
            return True
        else:
            return False

    def get_bound_level(self, actor):
        if self.is_in_bound(actor):
            return self.level


def convertHISM(actors, inVirtualTexture=None, sort=90):
    if actors is None:
        return None
    # blueprint
    bp_hism = unreal.EditorAssetLibrary.load_asset(
        '/Game/ArkGame/Environment/Houdini_Asset/roadSys/Blueprint/BP_roadSys_DecalInstance')
    # spawn actor
    loc = unreal.GameplayStatics.get_actor_array_average_location(actors)
    hismActor = unreal.EditorLevelLibrary.spawn_actor_from_object(bp_hism, loc)
    # get component
    hismComp = hismActor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    # set properties
    hismComp.set_static_mesh(actors[0].static_mesh_component.static_mesh)
    # add instance
    for actor in actors:
        trans = actor.get_actor_transform()
        hismComp.add_instance_world_space(trans)
        unreal.EditorLevelLibrary.destroy_actor(actor)

    unreal.log(type(hismComp))
    hismComp.set_editor_property('mobility', unreal.ComponentMobility.STATIC)
    unreal.log(type(hismComp))
    # bug: set_editor_property function will make the below function disable
    hismComp = hismActor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    hismComp.set_editor_property('translucency_sort_priority', sort)
    hismComp = hismActor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    hismComp.set_editor_property('runtime_virtual_textures', inVirtualTexture)
    hismComp = hismActor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    hismComp.set_cull_distances(505.0, 1100.0)
    # set tag
    hismActor.tags = actors[0].tags
    return hismActor


def get_decal_name_and_sort():
    roadSysDecalsTable = unreal.EditorAssetLibrary.load_asset('/HoudiniEngine/xPCG_Helper/Data/DT_RoadsysDecals')
    if isinstance(roadSysDecalsTable, unreal.DataTable):
        decalMeshColumns = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(roadSysDecalsTable, "DecalMesh")
        sortColumns = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(roadSysDecalsTable, "Sort")
        return [col.split('.')[-1][:-1] for col in decalMeshColumns], [int(sort) for sort in sortColumns]


def processing():
    unreal.log("processing!")

    # get decals and keep in the decals list
    actors = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                            unreal.StaticMeshActor)
    decals = []
    decal_assets = []
    actorFilter, actorSort = get_decal_name_and_sort()
    for actor in actors:
        if "xPCG_roadsys" in actor.get_actor_label() or 'xPCG_Roadsys' in actor.get_actor_label() :
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp:
                if comp.static_mesh.get_name() in actorFilter:
                    actor.tags = [unreal.Name('roadsys'), unreal.Name('roadsys_decal'), unreal.Name(comp.static_mesh.get_name())]
                    decals.append(actor)
                    if comp.static_mesh not in decal_assets:
                        decal_assets.append(comp.static_mesh)

    # get level bounds
    levelbounds = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                                 unreal.LevelBounds)

    # TODO : Hard Code, Change to auto get the sub levels.
    sublevelLevelBounds = []  # keep the level info
    levelNameFilter = ['GE_001_Basin_{}_{}'.format(x, y) for x in range(0, 5) for y in range(0, 5)]

    for bound in levelbounds:
        level = bound.get_outer()
        # unreal.log(level.get_path_name().split('.')[-1].split(':')[0])
        if level.get_path_name().split('.')[-1].split(':')[0] in levelNameFilter:
            mybound = myBound(bound)
            sublevelLevelBounds.append(mybound)
            # unreal.log(bound.get_actor_bounds(False))
            # unreal.log(level.get_path_name().split('.')[-1].split(':')[0])

    # get virtual texture
    virtualTextureVolumes = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(),
                                                                    unreal.RuntimeVirtualTextureVolume)
    virtualTexture = [vt.virtual_texture_component.virtual_texture for vt in virtualTextureVolumes]

    # set actor to level
    movedict = {}
    for decal in decals:
        index = sublevelLevelBounds.index(decal)     # use the __eq__ function
        if index >= 0:
            if movedict.get(sublevelLevelBounds[index].name):
                movedict.get(sublevelLevelBounds[index].name).append(decal)
            else:
                movedict[sublevelLevelBounds[index].name] = [decal]

    # move to the right level
    for k in movedict:
        # processing decals by levels
        if movedict[k]:
            streamingLevel = unreal.GameplayStatics.get_streaming_level(sublevelLevelBounds[index].level, k)
            # unreal.EditorLevelUtils.move_actors_to_level(movedict[k], streamingLevel)
            bp_hism_array = []
            # processing by the decal static mesh asset :
            for decal_asset in decal_assets:
                same_decal = unreal.EditorFilterLibrary.by_actor_tag(movedict[k], tag=decal_asset.get_name(),
                                                                filter_type=unreal.EditorScriptingFilterType.INCLUDE)
                if same_decal:
                    index = actorFilter.index(decal_asset.get_name())
                    current_sort = actorSort[index]
                    bp_hism_array.append(convertHISM(actors=same_decal, inVirtualTexture=virtualTexture,
                                                     sort=current_sort))

            if bp_hism_array:
                unreal.EditorLevelUtils.move_actors_to_level(bp_hism_array, streamingLevel)






# Processing !
processing()

