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
        start = []
        for i, groups in groupby(objects, key=lambda r: r['ID']):
            coord = []
            for group in groups:
                coord.append((group['X'], group['Y']))
            # collected the last points data
            ids.append(i)
            width.append(group['Width'])
            spline_type.append(group['SplineType'])
            start.append((group['X'], group['Y']))
            # collected the all points coords
            coords.append(coord)

        geo_dict = {'type': 'MultiLineString',
                    'coordinates': coords,
                    'ID': i,
                    'width': width,
                    'spline_type': spline_type,
                    'start': start
                    }

        return geo_dict


def get_intersections(multilines):
    intersections = []
    if isinstance(multilines, MultiLineString):
        linelist = [line for line in multilines.geoms]
    else:
        linelist = multilines

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
            for c in cross.geoms:
                distance = line.project(c)
                if distance > 0:
                    intersections.append(c)

    return intersections


def get_touch_lines(cross, lines):
    _touch_lines = []
    if isinstance(lines, MultiLineString):
        for line in lines.geoms:
            dist = cross.distance(line)
            if dist < 1.0 :
                _touch_lines.append(line)
    else:
        for road in lines:
            dist = cross.distance(road.line)
            if dist < 1.0:
                _touch_lines.append(road)
    # print("input lines num : {} ---- output lines num : {}".format(len(lines), len(_touch_lines)))
    return _touch_lines


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
        self.__roads = get_touch_lines(cross, multilines)
        self.__edges = self.get_edge_lines()
        self.__inters = self.get_edge_inters()
        self.__edge_splines = self.get_edge_splines()

    def get_edge_lines(self):
        edges = []
        for road in self.__roads:
            edges += road.get_road_edges()
        return edges

    def get_edge_inters(self):
        multi_edges = MultiLineString([road.line for road in self.__edges])
        return get_intersections(multi_edges)

    def get_edge_splines(self):
        edge_spline_list = []
        for inter in self.__inters:
            touch_road = get_touch_lines(inter, self.__edges)
            edge_spline_list.append(EdgeSpline(self.__cross, inter, touch_road))
        return edge_spline_list

    def get_spline_properties(self):
        properties = []
        for spline in self.__edge_splines:
            properties.append(spline.get_properties())
        return properties

    def draw(self):
        # draw lines
        if len(self.__roads) >0:
            for road in self.__roads:
                line = road.line
                plt.plot(line.xy[0], line.xy[1])
        # draw cross
        plt.scatter(self.__cross.x, self.__cross.y)

    def draw_edge_only(self, draw_ends=True):
        for edge in self.__edge_splines:
            edge.draw(draw_ends)


class EdgeSpline:
    def __init__(self, cross, inter, edges):
        self.__start_location = None
        self.__start_tangent = None
        self.__end_location = None
        self.__end_tangent = None
        self.cross = cross
        self.inter = inter
        self.edges = edges
        self.straights = self.get_straight_roads()
        self.endpoints = self.calc_properties()
        self.calc_properties()

    def get_straight_roads(self):
        straight_lines = []
        for edge in self.edges:
            dis = edge.line.project(self.inter)
            line1, line2 = cut(edge.line, dis)
            dis1, dis2 = self.cross.distance(line1), self.cross.distance(line2)
            if dis1 > dis2:
                straight_lines.append(RoadLine(line1, edge))
            else:
                straight_lines.append(RoadLine(line2, edge))
        return straight_lines

    def calc_properties(self):
        points = []
        for road in self.straights:
            line, width = road.line, road.width
            dist = line.project(self.inter)
            if dist < 1.0:
                end = line.interpolate(width)
            else:
                end = line.interpolate(dist - width)
            points.append(end)

        if len(points) == 2:
            start_loc = np.array(points[0].xy)
            end_loc = np.array(points[1].xy)
            start_tan = np.array(self.inter.coords.xy) - start_loc
            end_tan = np.array(self.inter.coords.xy) - end_loc
            self.set_properties(start_loc, start_tan, end_loc, end_tan)

        return points

    def set_properties(self, start_loc, start_tan, end_loc, end_tan):
        self.__start_location = start_loc
        self.__start_tangent = start_tan
        self.__end_location = end_loc
        self.__end_tangent = end_tan

    def get_properties(self):
        return {'start_location': [e[0] for e in self.__start_location.tolist()],
                'start_tangent': [e[0] for e in self.__start_tangent.tolist()],
                'end_location': [e[0] for e in self.__end_location.tolist()],
                'end_tangent': [e[0] for e in self.__end_tangent.tolist()]
                }

    def draw(self, draw_end=False):

        plt.scatter(self.inter.x, self.inter.y)
        for road in self.straights:
            plt.plot(road.line.xy[0], road.line.xy[1])
        if draw_end:
            for pts in self.endpoints:
                # print('Inter : {} -- Ends {}'.format(self.inter, pts))
                plt.scatter(pts.x, pts.y)


class RoadLine:
    def __init__(self, *args):
        if len(args) > 2:
            self.line, self.width, self.splineType, self.roadId = args
        else:
            line = args[0]
            road = args[1]
            self.line, self.width, self.splineType, self.roadId = line, road.width, road.splineType, road.roadId

    @classmethod
    def get_properties_from_json(cls, linestring, points_json, id):
        start_points = points_json['start']
        types = points_json['spline_type']
        widths = points_json['width']
        for i, pos in enumerate(start_points):
            pt = Point(pos)
            if pt.within(linestring):
                return cls(linestring, widths[i], types[i], id)

    def get_road_edges(self):
        side_l = self.line.parallel_offset(distance=self.width/2.0, side='left',
                                           resolution=16, join_style=1, mitre_limit=5.0)
        side_r = self.line.parallel_offset(distance=self.width/2.0, side='right',
                                           resolution=16, join_style=1, mitre_limit=5.0)
        return [RoadLine(side_l, self.width, self.splineType, self.roadId),
                RoadLine(side_r, self.width, self.splineType, self.roadId)]


def main():
    points_json = load_raodmap_json('roadmap_segment.json')  # read the roadmap json file
    lines = linemerge(shape(points_json))  # create shape and combine lines
    # create road line instance
    road_lines = []
    for i, line in enumerate(lines.geoms):
        road_lines.append(RoadLine.get_properties_from_json(line, points_json, i))
    # find the intersection
    cross_points = get_intersections(lines)
    # create cross area
    cross_area_list = []
    for cp in cross_points:
        cross_area = CrossArea(cp, road_lines)
        cross_area_list.append(cross_area)

    # draw
    property_content = []
    for ca in cross_area_list:
        property_content += ca.get_spline_properties()
        ca.draw_edge_only()
    # for prop in property_content:
        # print(prop)
    # show the graph
    plt.show()
    # write to json
    content = {}
    with open('output_cross_splines.json', 'w') as pf:
        content['spline'] = property_content
        json.dump(content, pf)


if __name__ == "__main__":
    main()