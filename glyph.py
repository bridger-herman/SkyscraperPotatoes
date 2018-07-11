#  Copyright 2018 Bridger Herman

#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:

#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import bpy
import sys
import time
import random
import importlib
from mathutils import Vector, Matrix

sys.path.append('.')

import blender_utils
importlib.reload(blender_utils)

NAME_PREFIX = "data_"
GLYPH_NAME = "data_glyph"

class Glyph:
    def __init__(self, value, normal):
        self.value = value
        self.normal = normal

class GlyphGenerator:
    # :obj: (bpy_struct Object)
    # :value_fn: (function with 3 args)
    def __init__(self, obj = None, value_fn = None):
        if obj == None:
            raise ValueError("No object passed in")
        if value_fn == None:
            raise ValueError("No value function passed in")
        self.value_fn = value_fn
        self.polygons = list(filter(lambda p: p.select, obj.data.polygons))
        if len(self.polygons) == 0:
            raise ValueError('No polygons selected!')
        self.edges = obj.data.edges
        self.vertices = obj.data.vertices
        self.bound_box = [Vector(vert) for vert in obj.bound_box]
        self.name = str(obj.name)
        self.cutoff = 20
        self.blend_obj = None

        # Find other vertex information
        self.vertex_indices = list(map(lambda v: v.index, self.vertices))

    # Join together all the data glyphs into one object
    def _join_data(self):
        bpy.ops.object.select_pattern(pattern = GLYPH_NAME + "*")
        bpy.ops.object.convert(target = 'MESH')
        bpy.ops.object.join()
        bpy.context.active_object.name = NAME_PREFIX + self.name
        bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
        self.blend_obj = bpy.context.active_object

    # Finds coordinates for a vertex of a given index, in the active mesh
    # :vert_index: (int) vertex index of the vertex we're finding coordinates for
    def _find_co(self, vert_index):
        try:
            desired = self.vertex_indices.index(vert_index)
        except ValueError:
            return (0, 0, 0)
        return tuple(self.vertices[desired].co)

    # Implemented by subclasses
    def within_fn(self, existing_point, new_point, current_polygon_vertices):
        return False

    # Implemented by subclasses
    def create_fn(self, points):
        return None

    # Distributes glyphs based on a Poission-Disc algorithm
    def distribute_poisson(self):
        print("Generating glyphs on selected mesh.")
        i = 0
        start_time = time.time()
        points_result = {}
        one_percent = int(len(self.polygons)/100.0) + 1
        for poly in self.polygons:
            try:
                i += 1
                if i % one_percent == 0:
                    print("Progress: {:.0%}".format(i / len(self.polygons)))
                num_within = 0
                vertex_coords = list(map(lambda vi: self._find_co(vi), poly.vertices))
                xt = blender_utils.extrema(vertex_coords)
                while num_within < self.cutoff:
                    point_inside_poly = blender_utils.random_inside(vertex_coords,
                            tuple(poly.normal), xt)
                    if point_inside_poly != None:
                        add = True
                        for p in points_result:
                            # Check if point is within diamater of another
                            # point (no overlaps allowed)
                            w = self.within_fn(p, point_inside_poly, vertex_coords)
                            if w:
                                add = False
                                num_within += 1
                                break
                        if add:
                            args = list(point_inside_poly) + \
                                    [self.value_fn(*point_inside_poly)]
                            fn_args = list(point_inside_poly) + list([vertex_coords])
                            points_result[point_inside_poly] = \
                                    Glyph(self.value_fn(*fn_args), poly.normal)
                            num_within = 0
            except KeyboardInterrupt:
                t1 = time.time()
                print("\nSampling finished at {:.2f}s".format(t1 - start_time))
                print("\nGenerated {} glyphs".format(len(points_result)))
                print("Joining...")
                self.create_fn(points_result)
                end_time = time.time()
                print("Join time {:.2f}s".format(end_time - t1))
                print("Total time: {:.2f}s".format(end_time - start_time))
                return points_result

        t1 = time.time()
        print("\nSampling finished at {:.2f}s".format(t1 - start_time))
        print("\nGenerated {} glyphs".format(len(points_result)))
        print("Joining...")
        self.create_fn(points_result)
        end_time = time.time()
        print("Join time {:.2f}s".format(end_time - t1))
        print("Total time: {:.2f}s".format(end_time - start_time))
        return points_result
