from shapely.geometry import *
from shapely.ops import *
import numpy as np
import matplotlib.pyplot as plt
import json
from itertools import groupby
import math


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
                    'ID': ids,
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


def round_coords(point_list):
    result = []
    for pt in point_list:
        x = round(pt.x)
        y = round(pt.y)
        result.append(Point(x, y))
    return result


def merge_intersections(point_list, tolerance=700.0):
    result = []
    for i in range(len(point_list)-1):
        current = point_list.pop()
        rest = MultiPoint(point_list)
        p0, p1 = nearest_points(current, rest)
        if p0.distance(p1) > tolerance:
            result.append(current)
    result += point_list
    return result


def get_touch_lines(point, lines, tolerance=1.0):
    _touch_lines = []
    if isinstance(lines, MultiLineString):
        for line in lines.geoms:
            dist = point.distance(line)
            if dist < tolerance:
                _touch_lines.append(line)
    else:
        for road in lines:
            dist = point.distance(road.line)
            if dist < tolerance:
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
                LineString(coords[:i + 1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]


class Inters:
    def __init__(self, point, radius, roads):
        self.point = point
        self.radius = radius
        self.roads = roads


class CrossArea:
    def __init__(self, cross, line_list):
        self.__cross = cross
        self.__roads = self.cross_road(line_list)
        self.__edges = self.get_edge_lines()
        self.__inters = self.get_edge_inters()
        self.__edge_splines = self.get_edge_splines()

    def cross_road(self, line_list):
        roads = get_touch_lines(self.__cross, line_list, 10.0)
        result = []
        for road in roads:
            dist = road.line.project(self.__cross)
            width = road.width
            position = dist - width * 2.0
            length = 0 if position < 0 else position
            line1, line2 = cut(road.line, length)
            line3 = get_touch_lines(self.__cross, MultiLineString([line1, line2]), 10.0)
            dist = line3[0].project(self.__cross)
            line1, line2 = cut(line3[0], (dist + width * 2.0))
            line6 = get_touch_lines(self.__cross, MultiLineString([line1, line2]), 10.0)
            touch_lines = get_touch_lines(self.__cross, MultiLineString(line6))
            for line in touch_lines:
                plt.plot(line.xy[0], line.xy[1])
            result += [RoadLine(line, road) for line in touch_lines]
        return result

    def confirm_edge_id(self):
        for road in self.__edges:
            width = road.width
            inters = road.line.intersection(self.__cross.buffer(width/4.0))
            a, b = inters.coords.xy[0], inters.coords.xy[-1]
            cat = math.atan2(b[1]-a[1], b[0]-a[0])
            r = (cat + math.pi) % math.pi
            road.roadId = r
        self.__edges = sorted(self.__edges, key=lambda x: x.roadId)

    def get_edge_lines(self):
        edges = []
        for road in self.__roads:
            edges += road.get_road_edges()
        return edges

    def get_edge_inters(self):
        multi_edges = sorted(self.__edges, key=lambda x: x.roadId)
        inters = get_intersections([edge.line for edge in multi_edges])
        multi_points = MultiPoint(inters)
        # filter points with cross area
        result = filter(self.__cross.buffer(self.__roads[0].width*2.0).contains, inters)
        inters = [r for r in result]
        # filter points with convex hull
        multi_points = MultiPoint(inters)
        convex = multi_points.convex_hull
        result = filter(convex.touches, inters)
        return [r for r in result]

    def get_edge_splines(self):
        edge_spline_list = []
        for inter in self.__inters:
            touch_road = get_touch_lines(inter, self.__edges)
            edge_spline_list.append(EdgeSpline(self.__cross, inter, touch_road, self.__roads))
        return edge_spline_list

    def get_spline_properties(self):
        properties = []
        for spline in self.__edge_splines:
            props = spline.get_properties()
            if props:
                properties.append(props)
        return properties

    def draw(self):
        # draw lines
        if len(self.__roads) > 0:
            for road in self.__roads:
                line = road.line
                plt.plot(line.xy[0], line.xy[1], scaley=False, scalex=False)
        # draw cross
        plt.scatter(self.__cross.x, self.__cross.y)

    def draw_edge_only(self, draw_ends=True):
        for edge in self.__edge_splines:
            edge.draw(draw_ends)


class EdgeSpline:
    def __init__(self, cross, inter, edges, roads):
        self.__start_location = None
        self.__start_tangent = None
        self.__end_location = None
        self.__end_tangent = None
        self.cross = cross
        self.inter = inter
        self.edges = edges
        self.roads = roads
        self.straights = self.get_straight_roads()
        self.endpoints = self.calc_properties()

    def get_straight_roads(self):
        straight_lines = []
        for edge in self.edges:
            dis = edge.line.project(self.inter)
            result = cut(edge.line, dis)
            if len(result) != 2:
                return None
            line1, line2 = result[0], result[1]
            # if the line and road lines are cross, we will remove it.
            multiroads = MultiLineString([road.line for road in self.roads])
            if line1.intersects(multiroads):
                if line2.intersects(multiroads):
                    # the special case : circle road will hit twice'
                    sub_inter1 = line1.intersection(multiroads)
                    if self.inter.buffer(self.roads[0].width*2.0).contains(sub_inter1):
                        straight_lines.append(RoadLine(line2, edge))
                    else:
                        straight_lines.append(RoadLine(line1, edge))
                else:
                    straight_lines.append(RoadLine(line2, edge))
            else:
                straight_lines.append(RoadLine(line1, edge))

        return straight_lines

    def calc_properties(self):
        points = []
        if self.straights is None:
            return None

        for road in self.straights:
            line, width = road.line, road.width
            dist = line.project(self.inter)
            if dist < 1.0:
                end = line.interpolate(width)
            else:
                end = line.interpolate(dist - width)
            points.append(end)

        if len(points) == 2:
            # be sure they are counter-clockwise order
            points.insert(1, self.inter)
            if LinearRing(points).is_ccw:
                points.reverse()

            start_loc = np.array(points[0].xy)
            end_loc = np.array(points[2].xy)
            start_tan = (np.array(self.inter.coords.xy) - start_loc) * 2.0
            end_tan = (end_loc - np.array(self.inter.coords.xy)) * 2.0
            self.set_properties(start_loc, start_tan, end_loc, end_tan)

        return points

    def set_properties(self, start_loc, start_tan, end_loc, end_tan):
        self.__start_location = start_loc
        self.__start_tangent = start_tan
        self.__end_location = end_loc
        self.__end_tangent = end_tan

    def get_properties(self):
        if self.__start_location is None:
            return None

        return {'start_location': [round(e[0], 2) for e in self.__start_location.tolist()],
                'start_tangent': [round(e[0], 2) for e in self.__start_tangent.tolist()],
                'end_location': [round(e[0], 2) for e in self.__end_location.tolist()],
                'end_tangent': [round(e[0], 2) for e in self.__end_tangent.tolist()]
                }

    def draw(self, draw_end=False):
        if self.straights is not None:
            plt.scatter(self.inter.x, self.inter.y)
            for road in self.straights:
                plt.plot(road.line.xy[0], road.line.xy[1], scaley=False, scalex=False)
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
            if not pt.disjoint(linestring):
                return cls(linestring, widths[i], types[i], id)

    def get_road_edges(self):
        side_l = self.line.parallel_offset(distance=self.width, side='left',
                                           resolution=16, join_style=1, mitre_limit=5.0)
        side_r = self.line.parallel_offset(distance=self.width, side='right',
                                           resolution=16, join_style=1, mitre_limit=5.0)
        return [RoadLine(side_l, self.width, self.splineType, self.roadId),
                RoadLine(side_r, self.width, self.splineType, self.roadId)]


def main():
    """ load Josn files """
    json_path = 'D:/NExTWorkSpace/ArkWorkSpace/Projects/Ark2019/Trunk/UE4NEXT_Stable/Engine/Plugins/Runtime/HoudiniEngine/Content/roadSys/'
    # json_path = 'D:/Foliage/'
    points_json = load_raodmap_json(json_path + 'roadmap_segment.json')  # read the roadmap json file
    '''create original line and merge them'''
    load_result = shape(points_json)
    lines = linemerge(load_result)  # create shape and combine lines
    """create road line instance"""
    road_lines = []
    for i, line in enumerate(lines.geoms):
        road_lines.append(RoadLine.get_properties_from_json(line, points_json, i))
    '''find the intersection'''
    cross_points = get_intersections(lines)
    cross_result = merge_intersections(cross_points)
    '''create cross area'''
    cross_area_list = []
    for cp in cross_result:
        cross_area = CrossArea(cp, road_lines)
        cross_area_list.append(cross_area)

    '''get properties'''
    property_content = []
    for ca in cross_area_list:
        property_content += ca.get_spline_properties()
        # ca.draw_edge_only()

    # output log
    # for prop in property_content:
    #     print(prop)
    # show the graph
    plt.axis("equal")
    plt.show()

    '''write to json'''
    content = {}
    with open('output_cross_splines.json', 'w') as pf:
        content['spline'] = property_content
        json.dump(content, pf)


if __name__ == "__main__":
    import time
    main()
    print('process time is {}'.format(time.process_time()))
