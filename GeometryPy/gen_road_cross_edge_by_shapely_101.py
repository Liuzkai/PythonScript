"""
Gen Road Edge by Shapely v 1.01
by zhongkailiu
creation data : 2022.4.8
Update Log :
2022.4.9 update:
1. separate line from mid of intersections [done]
2. add z coords for RoadLine [done]
3. clear useless code [done]
4. Filter the RoadLine type [done]
"""

from shapely.geometry import *
from shapely.ops import *
import numpy as np
import matplotlib.pyplot as plt
import json
from itertools import groupby
import math


class RoadLine:
    def __init__(self, *args):
        if len(args) > 2:
            self.line, self.width, self.splineType, self.roadId = args
        else:
            line = args[0]
            road = args[1]
            self.line = line
            self.width, self.splineType, self.roadId = road.width, road.splineType, road.roadId
        self.intersections = []

    @classmethod
    def get_properties_from_json(cls, linestring, points_json, Id):
        start_points = points_json['start']
        types = points_json['spline_type']
        widths = points_json['width']
        for i, pos in enumerate(start_points):
            pt = Point(pos)
            if not pt.disjoint(linestring):
                return cls(linestring, widths[i], types[i], Id)

    def get_road_edges(self):
        side_l = self.line.parallel_offset(distance=self.width, side='left',
                                           resolution=16, join_style=1, mitre_limit=5.0)
        side_r = self.line.parallel_offset(distance=self.width, side='right',
                                           resolution=16, join_style=1, mitre_limit=5.0)
        return [RoadLine(side_l, self.width, self.splineType, self.roadId),
                RoadLine(side_r, self.width, self.splineType, self.roadId)]

    def update_intersections_attribute(self, intersections_list, tolerance=2.0):
        for intersection in intersections_list:
            dist = intersection.distance(self.line)
            if dist < tolerance:
                self.intersections.append(intersection)


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
                    if self.inter.buffer(self.roads[0].width * 2.0).contains(sub_inter1):
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
        z = round(self.cross.z, 2)
        start_location = [round(e[0], 2) for e in self.__start_location.tolist()]
        start_tangent = [round(e[0], 2) for e in self.__start_tangent.tolist()]
        end_location = [round(e[0], 2) for e in self.__end_location.tolist()]
        end_tangent = [round(e[0], 2) for e in self.__end_tangent.tolist()]
        start_location.append(z)
        start_tangent.append(0.0)
        end_location.append(z)
        end_tangent.append(0.0)
        return {'start_location': start_location,
                'start_tangent': start_tangent,
                'end_location': end_location,
                'end_tangent': end_tangent
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


class CrossArea:
    def __init__(self, cross, line_list, filters):
        self.__cross = cross
        self.__roads = self.cross_road(line_list, filters)
        self.__edges = self.get_edge_lines()
        self.__inters = self.get_edge_inters()
        self.__edge_splines = self.get_edge_splines()

    def cross_road(self, line_list, filters):
        roads = get_touch_lines(self.__cross, line_list, filters['Width'])
        result = []
        for road in roads:
            dist = road.line.project(self.__cross)
            intersections = road.intersections
            if len(intersections) > 1:
                # when the road has more than one intersection
                sorted_inters = sorted(intersections, key=lambda x: road.line.project(x))
                total = len(sorted_inters)
                i = sorted_inters.index(self.__cross)
                if 0 < i < total-1:
                    start = (road.line.project(sorted_inters[i-1]) + dist) * 0.5
                    end = (road.line.project(sorted_inters[i+1]) + dist) * 0.5
                    result.append(RoadLine(cut_mid(road.line, start, end), road))
                elif i == 0:
                    start = 0
                    end = (road.line.project(sorted_inters[i+1]) + dist) * 0.5
                    result.append(RoadLine(cut_mid(road.line, start, end), road))
                elif i == total-1:
                    start = (road.line.project(sorted_inters[i-1]) + dist) * 0.5
                    end = road.line.length
                    result.append(RoadLine(cut_mid(road.line, start, end), road))
            else:
                # when the road has only one intersection
                result.append(road)

        if len(result) > 2:
            inters = get_intersections([road.line for road in result])
            if len(inters) > 1:
                points = MultiPoint(inters)
                centroid_coords = [points.centroid.x, points.centroid.y, self.__cross.z]
                self.__cross = Point(centroid_coords)
        return result

    def get_edge_lines(self):
        edges = []
        for road in self.__roads:
            edges += road.get_road_edges()
        return edges

    def get_edge_inters(self):
        inters = get_intersections([edge.line for edge in self.__edges])
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


def load_spline_json(path, **filters):
    with open(path, 'r') as fp:
        content = json.load(fp)
        if 'GameObjects' in content:
            objects = content['GameObjects']
        objects_filter = [e for e in objects
                          if e['Width'] > filters["Width"] and e['SplineType'] == filters['SplineType']]
        coords = []
        ids = []
        width = []
        spline_type = []
        start = []
        for i, groups in groupby(objects_filter, key=lambda r: r['ID']):
            coord = []
            for group in groups:
                coord.append((group['X'], group['Y'], group['Z']))
            # collected the last points data
            ids.append(i)
            width.append(group['Width'])
            spline_type.append(group['SplineType'])
            start.append((group['X'], group['Y'], group['Z']))
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
    for i in range(len(point_list) - 1):
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
            if cp.has_z:
                return [
                    LineString(coords[:i] + [(cp.x, cp.y, cp.z)]),
                    LineString([(cp.x, cp.y, cp.z)] + coords[i:])]
            else:
                return [
                    LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]


def cut_mid(line, start, end):
    if start > end:
        start, end = end, start
    coords = list(line.coords)
    line_pts = []
    start_pt = line.interpolate(start)
    end_pt = line.interpolate(end)
    line_pts.append(start_pt)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if start <= pd <= end:
            line_pts.append(Point(p))
    line_pts.append(end_pt)
    return LineString(line_pts)


def main():
    """ gen road edge script """
    ''' load Josn files '''
    # json_path = 'D:/NExTWorkSpace/ArkWorkSpace/Projects/Ark2019/Trunk/UE4NEXT_Stable/Engine/Plugins/Runtime/HoudiniEngine/Content/roadSys/'
    json_path = 'D:/Foliage/'
    filters = {'Width': 500.0, 'SplineType': 1}
    points_json = load_spline_json(json_path + 'roadmap_segment.json', **filters)  # read the roadmap json file

    '''create original line and merge them'''
    lines = linemerge(shape(points_json))  # create shape and combine lines

    '''find the intersection'''
    cross_result = merge_intersections(get_intersections(lines))

    '''create road line instance'''
    road_lines = []
    for i, line in enumerate(lines.geoms):
        roadline = RoadLine.get_properties_from_json(line, points_json, i)
        roadline.update_intersections_attribute(cross_result, roadline.width*0.5)
        if len(roadline.intersections) > 0:
            road_lines.append(roadline)

    '''draw intersections and roads'''
    # for line in lines.geoms:
    #     plt.plot(line.xy[0], line.xy[1])
    # for pt in cross_result:
    #     plt.scatter(pt.x, pt.y)

    '''create cross area'''
    cross_area_list = []
    for cp in cross_result:
        cross_area = CrossArea(cp, road_lines, filters)
        cross_area_list.append(cross_area)

    '''get properties'''
    property_content = []
    for ca in cross_area_list:
        property_content += ca.get_spline_properties()
        ca.draw()
        ca.draw_edge_only()

    # '''output log'''
    # for prop in property_content:
    #     print(prop)
    '''show the graph'''
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
