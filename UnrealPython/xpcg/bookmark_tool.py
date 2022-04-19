import unreal
import os






def add_camera_position_to_txt(name, all_cams):
    t, r = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
    path = unreal.Paths.project_config_dir()
    abs_path = unreal.Paths.convert_relative_path_to_full(path) + "ViewportTransform/"
    filename = abs_path + name + '.txt'
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)
    tf = str(t.x) + ',' + str(t.y) + ',' + str(t.z) + ',' + str(r.roll) + ',' + str(r.pitch) + ',' + str(r.yaw) + '\n'
    unreal.log(all_cams)
    unreal.log(tf)
    if tf not in all_cams:
        with open(filename, 'a+') as txt:
            txt.writelines(tf)
            txt.close()


def read_camera_position_from_txt(name):
    path = unreal.Paths.project_config_dir() + "ViewportTransform/"
    filename = path + name + '.txt'
    with open(filename, "r") as txt:
        readline = txt.readlines()
        txt.close()
    return readline


def set_camera(index, all_cams):
    tf = all_cams[index].split(',')
    t = unreal.Vector(float(tf[0]), float(tf[1]), float(tf[2]))
    r = unreal.Rotator(float(tf[3]), float(tf[4]), float(tf[5]))
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(t, r)


def process_camera(mode, all_cams, current):
    if mode == 1:
        current += 1
    else:
        current -= 1
    now = current % len(all_cams)
    set_camera(now, all_cams)
    return now


def remove_current_camera(name, all_cams, current):
    if len(all_cams) == 0:
        return current

    path = unreal.Paths.project_config_dir() + "ViewportTransform/"
    filename = path + name + '.txt'

    with open(filename, "w") as txt_w:
        for line_no, line in enumerate(all_cams, 0):
            if line_no == current:
                continue
            txt_w.write(line)
        txt_w.close()

    if current > 1:
        return current - 1
    else:
        return current


def load_viewport():
    path = unreal.Paths.project_config_dir() + "ViewportTransform/"
    abs_path = unreal.Paths.convert_relative_path_to_full(path)
    if not os.path.exists(abs_path):
        return ['default']
    files = os.listdir(abs_path)
    if len(files) == 0:
        return ['default']
    filename = []
    for f in files:
        filename.append(os.path.splitext(f)[0])
    return filename


def create_seq():
    path = unreal.Paths.project_config_dir() + "ViewportTransform/"
    abs_path = unreal.Paths.convert_relative_path_to_full(path)
    filename = 'viewport_default.txt'
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)
        txt_path = abs_path + filename
        f = open(txt_path, "w+")
        f.close()
    elif not os.path.exists(abs_path+filename):
        txt_path = abs_path + filename
        f = open(txt_path, "w+")
        f.close()
    else:
        files = os.listdir(abs_path)
        num = []
        for f in files:
            fn = os.path.splitext(f)[0]
            # unreal.log(fn[-2:])
            try:
                num.append(int(fn[-2:]))
            except Exception:
                pass
        new_one = 1
        while new_one in num:
            new_one += 1

        b = len(str(new_one))
        if b > 3:
            filename = 'viewport_seq%05d.txt' % new_one
        filename = 'viewport_seq%02d.txt' % new_one
        txt_path = abs_path + filename
        f = open(txt_path, "w+")
        f.close()
    return filename.replace(".txt","")


def remove_seq(name):


    if name == 'viewport_default':
        return
    path = unreal.Paths.project_config_dir() + "ViewportTransform/"
    filename = name+".txt"
    file_path = path + filename
    if not os.path.exists(file_path):
        return
    os.remove(file_path)


def screen_snapshot(seq_name, camera_index):
    image_index = 1
    file_name = "{}_{:d}_{:d}".format(seq_name, camera_index, image_index)
    path = unreal.Paths().screen_shot_dir() + file_name + ".png"
    while os.path.exists(path):
        image_index += 1
        file_name = "{}_{:d}_{:d}".format(seq_name, camera_index, image_index)
        path = unreal.Paths().screen_shot_dir() + file_name + ".png"

    unreal.AutomationLibrary().take_high_res_screenshot(1920, 1080, file_name)


def screen_stats_save(seq_name,camera_index,export_path):
    image_index = 1
    file_name = "{}_{:d}_{:d}.csv".format(seq_name, camera_index, image_index)
    save_path = unreal.Paths().convert_relative_path_to_full(export_path) + "/"
    path = save_path + file_name
    unreal.log_warning("csv file path : {}".format(path))
    while os.path.exists(path):
        image_index += 1
        file_name = "{}_{:d}_{:d}.csv".format(seq_name, camera_index, image_index)
        path = save_path + file_name

    out = file_name
