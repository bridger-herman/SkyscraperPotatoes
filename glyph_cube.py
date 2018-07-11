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
import importlib
from mathutils import Vector

sys.path.append('.')

import mapper
importlib.reload(mapper)
LinearMapper= mapper.LinearMapper

import glyph
importlib.reload(glyph)
from glyph import *

import blender_utils
importlib.reload(blender_utils)

class CubeGenerator(GlyphGenerator):
    '''Generic box-shaped glyphs'''
    def _create_cube(self, location, value, normal = (0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(radius=value, location=location)
        ob = bpy.context.active_object
        ob.name = GLYPH_NAME
        closest_vertex, _ = nearest_vertex(self.vertices, Vector(location))
        gradient = gradient_at_vertex_2(self.edges, self.vertices, closest_vertex)
        blender_utils.rotate_obj_gradient(ob, normal, gradient)

    def _create_cubes(self, locations):
        total = len(locations)
        for (i, point) in enumerate(locations):
            print("Progress: {:.0%}".format(i / total))
            self._create_cube(point, locations[point].value, locations[point].normal)
        self._join_data()

    def create_fn(self, points):
        return self._create_cubes(points)

class HeightCubeGenerator(CubeGenerator):
    '''Glyphs based on height'''
    def _create_cube(self, location, value, normal=(0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(radius=1, location=location)
        ob = bpy.context.active_object
        ob.name = GLYPH_NAME
        closest_vertex, _ = nearest_vertex(self.vertices, Vector(location))
        gradient = gradient_at_vertex_2(self.edges, self.vertices, closest_vertex)
        blender_utils.rotate_obj_gradient(ob, normal, gradient)
        ob.scale[0] = 0.75
        ob.scale[1] = 0.75
        ob.scale[2] = value * 1.15
        ob.location += 0.85 * value * Vector(normal)

    def within_fn(self, existing_point, new_point, current_polygon_vertices):
        # Radius is 1; use 3 for buffer
        return blender_utils.within_cube(existing_point, new_point, 4)

class LengthCubeGenerator(CubeGenerator):
    '''Glyphs following the gradient'''
    def _create_cube(self, location, value, normal=(0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(radius=1, location=location)
        ob = bpy.context.active_object
        ob.name = GLYPH_NAME
        closest_vertex, _ = nearest_vertex(self.vertices, Vector(location))
        gradient = gradient_at_vertex_2(self.edges, self.vertices, closest_vertex)
        blender_utils.rotate_obj_gradient(ob, normal, gradient)
        ob.scale[1] = value

    def within_fn(self, existing_point, new_point, current_polygon_vertices):
        fn_args = list(new_point) + list([current_polygon_vertices])
        value = self.value_fn(*fn_args)
        return blender_utils.within_cube(existing_point, new_point, 5)

class LengthCubeGenerator2(CubeGenerator):
    '''Glyphs following the perpendicular gradient'''
    def _create_cube(self, location, value, normal=(0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(radius=1, location=location)
        ob = bpy.context.active_object
        ob.name = GLYPH_NAME
        closest_vertex, _ = nearest_vertex(self.vertices, Vector(location))
        gradient = gradient_at_vertex_2(self.edges, self.vertices, closest_vertex)
        blender_utils.rotate_obj_gradient(ob, normal, gradient)
        ob.scale[0] = value

    def within_fn(self, existing_point, new_point, current_polygon_vertices):
        fn_args = list(new_point) + list([current_polygon_vertices])
        value = self.value_fn(*fn_args)
        return blender_utils.within_cube(existing_point, new_point, 5)

class SizeCubeGenerator(CubeGenerator):
    def within_fn(self, existing_point, new_point, current_polygon_vertices):
        fn_args = list(new_point) + list([current_polygon_vertices])
        value = 2.5*self.value_fn(*fn_args)
        recip_value = 1/value
        return blender_utils.within_cube(existing_point, new_point, value + recip_value)
