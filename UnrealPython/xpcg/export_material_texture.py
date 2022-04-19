import unreal


def get_asset_dependencies(asset_data,
                           include_hard_management_references=True,
                           include_hard_package_references=True,
                           include_searchable_names=False,
                           include_soft_management_references=False,
                           include_soft_package_references=False):
    '''
    :param asset_data: unreal.AssetData class
    :param include_hard_management_references: (bool): [Read-Write] Reference that says one object directly manages another object, set when Primary Assets manage things explicitly
    :param include_hard_package_references: (bool): [Read-Write] Dependencies which are required for correct usage of the source asset, and must be loaded at the same time
    :param include_searchable_names: (bool): [Read-Write] References to specific SearchableNames inside a package
    :param include_soft_management_references: (bool): [Read-Write] Indirect management references, these are set through recursion for Primary Assets that manage packages or other primary assets
    :param include_soft_package_references: (bool): [Read-Write] Dependencies which don't need to be loaded for the object to be used (i.e. soft object paths)
    :return: reference path(str)
    '''
    if isinstance(asset_data, unreal.AssetData):
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        asset_registry_option = unreal.AssetRegistryDependencyOptions(include_hard_management_references,
                                                                      include_hard_package_references,
                                                                      include_searchable_names,
                                                                      include_soft_management_references,
                                                                      include_soft_package_references)

        dependencies_hard = asset_registry.get_dependencies(asset_data.package_name, asset_registry_option)
        reference_hard = asset_registry.get_referencers(asset_data.package_name, asset_registry_option)

        unreal.log("================dependencies_hard===============")
        for item in dependencies_hard:
            unreal.log(item)

        return dependencies_hard


# assets = unreal.EditorUtilityLibrary.get_selected_asset_data()
# for asset in assets:
#     dep = get_asset_dependencies(asset)

