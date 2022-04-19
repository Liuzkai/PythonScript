import unreal


def get_asset_reference():
    assets = unreal.EditorUtilityLibrary.get_selected_asset_data()
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry_option = unreal.AssetRegistryDependencyOptions()
    asset_registry_option.include_soft_package_references = True
    asset_registry_option.include_hard_package_references = True

    dependencies_hard = asset_registry.get_dependencies(assets[0].package_name, asset_registry_option)
    reference_hard = asset_registry.get_referencers(assets[0].package_name, asset_registry_option)

    unreal.log("================dependencies_hard===============")
    for item in dependencies_hard:
        unreal.log(item)

    unreal.log("================reference_hard===============")
    for item in reference_hard:
        unreal.log(item)