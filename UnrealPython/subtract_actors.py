#
# Unreal Engine 5.0 Python Script that takes in N >= 2 selected StaticMesh Actors,
# and subtracts Actors 1..N from the first Actor
#

import unreal

# output path and asset name (random suffix will be appended)
BooleanResultBasePath = "/Game/PythonBooleanTest"
BooleanResultBaseName = "PyBoolean"

# get Actor subsystem and get set of selected Actors
actorSub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SelectedActors = unreal.EditorFilterLibrary.by_class(actorSub.get_selected_level_actors(), unreal.StaticMeshActor)

# make temporary structs
asset_options = unreal.GeometryScriptCopyMeshFromAssetOptions()
requested_lod = unreal.GeometryScriptMeshReadLOD()
copy_from_component_options = unreal.GeometryScriptCopyMeshFromComponentOptions()

# loop over Actors. Collect meshes, subtract all other meshes from the first mesh
i = 0
ResultMesh = unreal.DynamicMesh()       # final mesh will be here
ResultMaterials = []                    # final material list will be here
LocalToWorld = unreal.Transform()       # ResultMesh will be in World space, and this will be the transformation back to local space of the first Actor
for StaticMeshActor in SelectedActors:
    StaticMeshComponent = StaticMeshActor.static_mesh_component
    StaticMesh = StaticMeshComponent.static_mesh
    
    # if it's mesh 0, just copy it into ResultMesh, otherwise subtract it
    if i == 0:
        # copy static mesh to dynamic mesh
        (ResultMeshOut, LocalToWorld, Outcome) = unreal.GeometryScript_SceneUtils.copy_mesh_from_component(StaticMeshComponent, ResultMesh, copy_from_component_options, True)

        # create flattened list of materials from this StaticMesh Component (note that we must use asset sections to figure out correct material slot index!)
        (AssetMaterialList, MaterialIndices, Outcome) = unreal.GeometryScript_AssetUtils.get_section_material_list_from_static_mesh(StaticMesh, unreal.GeometryScriptMeshReadLOD() )
        for matidx in MaterialIndices:
            ResultMaterials.append( StaticMeshComponent.get_material(matidx) )      # use Component material instead of Asset material!
    else:
        # copy static mesh to dynamic mesh
        TempMesh = unreal.DynamicMesh()
        unreal.GeometryScript_SceneUtils.copy_mesh_from_component(StaticMeshComponent, TempMesh, copy_from_component_options, True)
        
        # create flattened list of materials from this StaticMesh Component (note that we must use asset sections to figure out correct material slot index!)
        (AssetMaterialList, MaterialIndices, Outcome) = unreal.GeometryScript_AssetUtils.get_section_material_list_from_static_mesh(StaticMesh, unreal.GeometryScriptMeshReadLOD() )
        MaterialIndices.reverse()       # reverse list so that we can process material IDs from largest to smallest and avoid collision, as we will always remap to larger
        for matidx in MaterialIndices:
            new_matidx = len(ResultMaterials)
            ResultMaterials.append( StaticMeshComponent.get_material(matidx) )      # use Component material instead of Asset material!
            unreal.GeometryScript_Materials.remap_material_i_ds( TempMesh, matidx, new_matidx )
        
        # do the boolean subtract operation
        subtract_options = unreal.GeometryScriptMeshBooleanOptions()
        unreal.GeometryScript_MeshBooleans.apply_mesh_boolean(ResultMesh, unreal.Transform(), TempMesh, unreal.Transform(), unreal.GeometryScriptBooleanOperation.SUBTRACT, subtract_options)
        
    i = i + 1

# apply inverse transform to ResultMesh, becase it was transformed to world
unreal.GeometryScript_MeshTransforms.transform_mesh(ResultMesh, LocalToWorld.inverse())

if ResultMesh.get_triangle_count() > 0:
    # generate a unique new asset name, so that we don't lose the output due to a name collision
    NewAssetNameOptions = unreal.GeometryScriptUniqueAssetNameOptions()
    (NewAssetPath, NewAssetName, Success) = unreal.GeometryScript_NewAssetUtils.create_unique_new_asset_path_name(BooleanResultBasePath, BooleanResultBaseName, NewAssetNameOptions)
    # create a new asset for the output mesh
    NewAssetOptions = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    # NewAssetOptions.enable_nanite = True       # can use this to enable Nanite
    (NewStaticMesh, Outcome) = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(ResultMesh, NewAssetPath, NewAssetOptions)
    if Outcome == unreal.GeometryScriptOutcomePins.SUCCESS:
        # in 5.0 the create-new-asset function does not support setting materials, so now copy it again (could also enable nanite here)
        UpdateAssetOptions = unreal.GeometryScriptCopyMeshToAssetOptions()
        UpdateAssetOptions.replace_materials = True
        UpdateAssetOptions.new_materials = ResultMaterials
        unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(ResultMesh, NewStaticMesh, UpdateAssetOptions, unreal.GeometryScriptMeshWriteLOD())
else:
    print('Result Mesh is Empty!') 
