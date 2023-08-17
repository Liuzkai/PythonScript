import unreal as ue

def rtx_env_setup():
    cmds = [#'r.Shadow.EnableShadowMaskTextureArray 0',  # RTX bug, Avoid of crash when opening sequence while rtx on
            'r.ShadowQuality 4',    # high quality shadow
            'r.Shadow.MaxCSMResolution 2048',   # shadow map resolution
            'r.Shadow.ForceDisableCache 1',
            'r.forcelod 0'
            ]

    for cmd in cmds:
        ue.SystemLibrary.execute_console_command(None, cmd, None)


if __name__ == "__main__":
    rtx_env_setup()