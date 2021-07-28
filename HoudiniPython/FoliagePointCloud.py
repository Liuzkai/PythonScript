import hou


def Read_Point_Cloud():
    import csv

    node = hou.pwd()
    geo = node.geometry()
    attrib_path = geo.addAttrib(hou.attribType.Point, "path", "")
    attrib_name = geo.addAttrib(hou.attribType.Point, "name", "")
    attrib_trans = geo.addAttrib(hou.attribType.Point, "trans",
                                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    attrib_height = geo.addAttrib(hou.attribType.Point, "height", 0.0)
    attrib_radius = geo.addAttrib(hou.attribType.Point, "radius", 0.0)
    project_path = node.parm('unreal_project').evalAsString()
    csv_path = project_path + '/Saved/foliageInstance.csv'
    with open(csv_path, "rb") as foliage_csv:
        rs = csv.reader(foliage_csv)
        for r in rs:
            if len(r[0]) < 1:
                continue
            new_pt = geo.createPoint()
            new_pt.setAttribValue(attrib_path, r[0])
            new_pt.setAttribValue(attrib_name, r[0].split('.')[-1])
            new_pt.setAttribValue(attrib_trans, [float(r[1]), float(r[2]), float(r[3]), float(r[4]),
                                                 float(r[5]), float(r[6]), float(r[7]), float(r[8]),
                                                 float(r[9]), float(r[10]), float(r[11]), float(r[12]),
                                                 float(r[13]), float(r[14]), float(r[15]), float(r[16])])
            new_pt.setAttribValue(attrib_height, float(r[17]))
            new_pt.setAttribValue(attrib_radius, float(r[18]))
        foliage_csv.close()


def Read_CSV():
    import os
    import csv

    node = hou.pwd()
    geo = node.geometry()
    isNothing = node.parm("nothing").evalAsInt()
    geo_name = geo.addAttrib(hou.attribType.Point, "name", "Invaild Name")
    geo_path = geo.addAttrib(hou.attribType.Point, "path", "")
    geo_radius = geo.addAttrib(hou.attribType.Point, "radius", 0.0)
    geo_height = geo.addAttrib(hou.attribType.Point, "height", 0.0)

    path = node.parm('file').evalAsString()
    with open(path) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
        names = []
        paths = []
        radius = []
        heights = []
        for row in f_csv:
            try:
                rad = float(row[2]) * 0.5
                geo.createPoint()
                names.append(row[0])
                path_str = row[1] if isNothing == 0 else ""
                paths.append(path_str)
                radius.append(rad)
                heights.append(float(row[3]))
            except ValueError:
                continue

        names_tuple = tuple(names)
        path_tuple = tuple(paths)
        rad_tuple = tuple(radius)
        hei_tuple = tuple(heights)
        geo.setPointStringAttribValues("name", names_tuple)
        geo.setPointStringAttribValues("path", path_tuple)
        geo.setPointFloatAttribValues("radius", rad_tuple)
        geo.setPointFloatAttribValues("height", hei_tuple)


def Read_Table():
    import csv
    node = hou.pwd()
    geo = node.geometry()
    # create attributes
    geo.addAttrib(hou.attribType.Point, "source", "")
    geo.addAttrib(hou.attribType.Point, "target", "")
    geo.addAttrib(hou.attribType.Point, "percent", 0.0)
    # Read File
    path = node.parm('path').evalAsString()

    with open(path) as f:
        f_csv = csv.reader(f)

        headers = next(f_csv)
        source = []
        target = []
        percent = []
        for row in f_csv:
            try:
                if row[0] == 'source' or row[0] == '' or row[1] == '' or row[3] == '':
                    continue
                else:
                    source.append(row[0])
                    target.append(row[1])
                    percent.append(float(row[3]))
                    geo.createPoint()
            except ValueError:
                continue

        source_tuple = tuple(source)
        target_tuple = tuple(target)
        percent_tuple = tuple(percent)
        geo.setPointStringAttribValues("source", source_tuple)
        geo.setPointStringAttribValues("target", target_tuple)
        geo.setPointFloatAttribValues("percent", percent_tuple)




def create_table(kwargs):
    import csv
    import os.path as os_p
    from itertools import izip_longest
    from collections import Counter
    # geometry data
    node = kwargs['node']
    target = node.node('unreal_asset')
    source = node.node('Point_Cloud')
    t_geo = target.geometry()
    s_geo = source.geometry()
    t_name = t_geo.findPointAttrib('name').strings()
    s_name = s_geo.findPointAttrib('name').strings()
    # create file
    file_path = node.parm('foliage_type').evalAsString().replace('.csv', '_table_0.csv')
    file_index = 1
    new_file_path = file_path
    while os_p.isfile(new_file_path):
        n = '_table_{}.csv'.format(file_index)
        new_file_path = file_path.replace('_table_0.csv', n)
        file_index += 1

    # count the amount of each of name points
    all_name = s_geo.pointStringAttribValues('name')
    all_count = Counter(all_name)

    file = open(new_file_path, 'wb')
    w = csv.writer(file)
    # header
    s_l = ['source']
    t_l = ['target']
    a_l = ['amount']
    p_l = ['percent']
    # data
    s_l += list(s_name)
    for n in s_name:
        if n in t_name:
            t_l.append(n)
        else:
            t_l.append('')
    for n in t_name:
        if n not in t_l:
            t_l.append(n)

    a_l += [all_count[n] for n in s_name]
    p_l += [1.0 for i in range(0, max(len(s_l), len(t_l)) - 1)]
    # compose the rows
    lis = list([s_l, t_l, a_l, p_l])
    l = list(izip_longest(*lis, fillvalue=''))
    # write data
    w.writerows(l)
    file.close()


def force_load_file(kwargs):
    node = kwargs['node']
    node.node('Read_Point_Cloud').cook(True)
    node.node('Read_CSV').cook(True)
    node.node('Replace_and_Remove').cook(True)

###################################################################################
from collections import namedtuple
import random
import csv

FoliageTable = namedtuple("FoliageTable", "source target percent")

def Replace_and_Remove():
    # point cloud
    node = hou.pwd()
    geo = node.geometry()

    # name_attrib = geo.findPointAttrib('name')
    # name = name_attrib.strings()[0]

    # target table
    tnode = node.inputs()[1]
    tgeo = tnode.geometry()

    tnames = tgeo.pointStringAttribValues('name')

    # read replace table
    f_path = node.parm('path').evalAsString()
    f_file = open(f_path, 'rb')
    rows = []
    for row in csv.reader(f_file):
        rows.append(row)
    f_file.close()

    # create the dict for table
    foliage_table = {}
    for r in rows:
        if r[0] == 'source' or r[0] == '' or r[1] == '' or r[3] == '':
            continue
        if r[0] == name and r[1] in tnames:
            if r[0] in foliage_table:
                foliage_table[r[0]] += [FoliageTable(r[0], r[1], r[3])]
            else:
                foliage_table[r[0]] = [FoliageTable(r[0], r[1], r[3])]
    # print foliage_table["SM_Tree_Birch_Small05"].percent

    # processing every point (maybe slow?)
    # to_delete_pts = []
    # for pt in geo.points():
    #     pt_name = pt.attribValue("name")
    #     if pt_name not in foliage_table:
    #         to_delete_pts.append(pt)
    #     else:
    #         tables = foliage_table[pt_name]
    #         if len(tables) > 1:
    #             total_percent = sum([float(t.percent) for t in tables])
    #             # total_percent = total_percent if total_percent > 1.0 else 1.0/total_percent
    #             # target_pool = []
    #             # for t in tables:
    #             #     target_pool += [t.target] * int(float(t.percent) / total_percent * 100.0)
    #             # final_target = random.choice(target_pool)
    #
    #
    #             pt.setAttribValue("name", str(len(target_pool)))
    #         else:
    #             pt.setAttribValue("name", tables[0].target)

    # processing every name


    geo.deletePoints(to_delete_pts)


