

import unreal as ue


def menus_setup():

    menus = ue.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")  # 获取unreal的菜单控件

    added_menu = main_menu.add_sub_menu(main_menu.get_name(), "PV", "PVTools", "PVTools", 'PV Team Toolset')  # 添加子菜单

    # 环境设置按钮
    entry = ue.ToolMenuEntry(
        name='setup',
        type=ue.MultiBlockType.MENU_ENTRY,
        insert_position=ue.ToolMenuInsert('', ue.ToolMenuInsertType.DEFAULT)
    )  # 按钮
    entry.set_label('环境设置')
    entry.set_string_command(ue.ToolMenuStringCommandType.PYTHON, "Name", '../../../../Client/PyScript/PV/PVRTXEnv.py')  # 设置按钮的功能

    added_menu.add_menu_entry('PV', entry)  # 将按钮添加到子菜单


    # 开启录制工具按钮
    recorder_entry = ue.ToolMenuEntry(
        name='run_recorder',
        type=ue.MultiBlockType.MENU_ENTRY,
        insert_position=ue.ToolMenuInsert('setup', ue.ToolMenuInsertType.DEFAULT)
    )  # 按钮
    recorder_entry.set_label('开启录制工具')
    recorder_entry.set_string_command(ue.ToolMenuStringCommandType.PYTHON, "Name", '../../../../Client/PyScript/PV/PVRecorderRun.py')  # 设置按钮的功能

    added_menu.add_menu_entry('PV', recorder_entry)  # 将按钮添加到子菜单

    # 重置位移工具按钮

    RestTf_entry = ue.ToolMenuEntry(
        name='rest_transform',
        type=ue.MultiBlockType.MENU_ENTRY,
        insert_position=ue.ToolMenuInsert('setup', ue.ToolMenuInsertType.DEFAULT)
    )  # 按钮
    RestTf_entry.set_label('重置所选物体位移')
    RestTf_entry.set_string_command(ue.ToolMenuStringCommandType.PYTHON, "Name", '../../../../Client/PyScript/PV/PVRestTransform.py')  # 设置按钮的功能

    added_menu.add_menu_entry('PV', RestTf_entry)  # 将按钮添加到子菜单

    menus.refresh_all_widgets()  # 刷新菜单ui



if __name__ == "__main__":
    menus_setup()
