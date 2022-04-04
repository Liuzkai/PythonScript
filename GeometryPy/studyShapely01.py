from shapely.geometry import *
import numpy as np
import matplotlib.pyplot as plt
import json
from itertools import groupby


class spline:

    def __init__(self, points_dict):
        self.__geo_interface__ = points_dict


def load_raodmap_json(path):
    with open(path, 'r') as fp:
        content = json.load(fp)
        if 'GameObjects' in content:
            objects = content['GameObjects']

        coords = []
        coord = []
        ids = []
        width = []
        spline_type = []

        for id, groups in groupby(objects, key=lambda r: r['ID']):
            coord = []
            for group in groups:
                coord.append((group['X'], group['Y']))
                ids.append(group['ID'])
                width.append(group['Width'])
                spline_type.append(group['SplineType'])
            coords.append(coord)

        geo_dict = {'type': 'MultiLineString',
                    'ID': id,
                    'width': width,
                    'spline_type': spline_type,
                    'coordinates': coords}

        return geo_dict


def main():
    points_json = load_raodmap_json('roadmap_segment.json')
    lines = shape(points_json)
    rlines = [line for line in lines.geoms]
    for i in range(len(rlines)):
        cline = rlines.pop()
        cross = cline.intersection(MultiLineString(rlines))

        if isinstance(cross, Point):
            pass
            # plt.scatter(cline.xy[0], cline.xy[1])
            # print("singlepoint: line is contains {} is {}, distance is {}".format(cross, cross.within(cline), cline.project(cross)))
            # print("singlepoint: line is contains {} is {}, distance is {}".format(cross, cross.within(cline), cline.project(cross)))
            # if not cline.touches(cross):
            #     plt.plot(cline.xy[0], cline.xy[1])
            #     # plt.scatter(cross.x, cross.y)

        elif isinstance(cross, MultiPoint):
            for point in cross.geoms:
                print(cline)
                print(point)
                print("multipoints: line is contains {} is {}, distance is {}".format(point, point.within(cline), cline.project(point)))
                # if not cline.touches(point):
                plt.plot(cline.xy[0], cline.xy[1], scalex=False, scaley=False)
                plt.scatter(point.x, point.y)
    # for l in lines.geoms:
    #     x, y = l.xy
    #     plt.plot(x, y)

    plt.show()


if __name__ == "__main__":
    main()