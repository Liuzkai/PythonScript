# _*_ coding: utf-8 _*_
# @FileName:PVDebug
# @Data:2024-05-27 : 09 : 59
# @Author:zhongkailiu
# @Contact:zhongkailiu@tencent.com
import unreal





print('+++++++++ pv debug Start +++++++++')
asset_datas = unreal.EditorUtilityLibrary.get_selected_asset_data()
for asset_data in asset_datas:
    asset = asset_data.get_asset()

print('--------- pv debug End ---------')