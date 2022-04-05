from shapely.geometry import *
import numpy as np
import matplotlib.pyplot as plt
import json
from itertools import groupby
from shapely.ops import *


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
                    'coordinates': coords }

        return geo_dict


def get_intersections(multilines):
    intersections = []
    linelist = [line for line in multilines.geoms]
    if linelist is None:
        return intersections
    # find the intersected points
    for i in range(len(linelist) - 1):
        line = linelist.pop()
        cross = line.intersection(MultiLineString(linelist))
        if isinstance(cross, Point):
            distance = line.project(cross)
            if distance > 0:
                intersections.append(cross)

        elif isinstance(cross, MultiPoint):
            for c in cross:
                distance = line.project(cross)
                if distance > 0:
                    intersections.append(c)

    return intersections



def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]


class CrossArea:
    def __init__(self, cross, multilines):
        self.__cross = cross
        self.__lines = self.get_touch_lines(multilines)
        self.__edges = []

    def get_touch_lines(self, lines):
        _edges = []
        for line in lines.geoms:
            snaped = snap(self.__cross, line, 1.0)
            if self.__cross.equals_exact(snaped, 1.0):
                _edges.append(line)
        return _edges

    def draw(self):
        # draw lines
        for line in self.__lines:
            plt.plot(line.xy[0], line.xy[1])
        # draw cross
        plt.scatter(self.__cross.x, self.__cross.y)


class EdgeLine:
    def __init__(self, start_loc, start_tan, end_loc, end_tan):
        self.__start_location = start_loc
        self.__start_tangent = start_tan
        self.__end_location = end_loc
        self.__end_tangent = end_tan


def main():
    points_json = load_raodmap_json('roadmap_segment.json') # read the roadmap json file
    lines = linemerge(shape(points_json))  # create shape and combine lines
    # find the intersection
    cross_points = get_intersections(lines)
    # create cross area
    cross_area_list = []
    for cp in cross_points:
        cross_area_list.append(CrossArea(cp, lines))

    # draw
    for ca in cross_area_list:
        ca.draw()

    # show the graph
    plt.show()


if __name__ == "__main__":
    main()