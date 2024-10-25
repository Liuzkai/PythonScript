import unreal as ue
import os
import glob

MapsPath = ue.Paths.convert_relative_path_to_full(ue.Paths.project_content_dir()) + 'Maps/'
MapsSet = [map for map in os.listdir(MapsPath) if map[:4] == u'NGR_']


# MapsPath = '/Game/Maps/NGR_EastWorld_Dungeon/NGR_EastWorld_Dungeon_01'
# Levels = ue.EditorAssetLibrary.list_assets(MapsPath)
# if len(Levels) is not 0:
#     print(Levels[0])
#     print(ue.EditorAssetLibrary.get_tag_values(Levels[0]))
