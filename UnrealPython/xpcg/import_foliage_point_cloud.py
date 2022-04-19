import unreal


# get the selected asset
assets = unreal.EditorUtilityLibrary.get_selected_assets()
asset = assets[0] if assets else None
