import unreal as ue


def run_recorder():
    recorder_asset = ue.EditorAssetLibrary.load_asset("/Game/Editor/GameRecoder/RecordMain.RecordMain")
    editor_utility_subsystem = ue.EditorUtilitySubsystem()
    editor_utility_subsystem.spawn_and_register_tab(recorder_asset)



if __name__ == "__main__":
    run_recorder()