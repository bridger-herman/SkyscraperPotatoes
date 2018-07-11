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
import math
import random
import importlib
from mathutils import Vector

# Other imports
sys.path.append(".")

import mesh_helpers
importlib.reload(mesh_helpers)
from mesh_helpers import make_tag

# Get the spherical coordinates of an (x, y, z) coordinate
def _to_spherical(co):
    x, y, z = co
    r = (x**2 + y**2 + z**2)**0.5
    theta = math.atan2(y, x)
    assert r != 0
    phi = math.acos(z/r)
    return Vector((r, theta, phi))

# Get the (x, y, z) coordinate from a spherical
def _to_xyz(co):
    r, theta, phi = co
    x = r * math.cos(theta) * math.sin(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(phi)
    return Vector((x, y, z))

class Potato:
    '''A randomly generated potato blob'''
    NUM_POTATOES = 0
    def __init__(self, pos=Vector((0, 0, 0)),
            peak_probability=0.10,
            max_peak_height=90,
            base_size=40,
            resolution=128,
            smooth_factor=1.5,
            smooth_steps=12,
            margin=5,
            tag_id='{:03d}'.format(NUM_POTATOES),
            name='potato'):
        self.pos = pos
        self.margin = margin
        self.resolution = resolution
        self.smooth_factor = smooth_factor
        self.smooth_steps = smooth_steps
        self.peak_probability = peak_probability
        self.base_size = base_size
        self.max_peak_height = max_peak_height
        self.tag_id = tag_id
        self.name = '{}_{}'.format(name, tag_id)
        self.blend_obj = None

    def generate(self):
        '''Actually generate the mesh for the potato'''
        bpy.ops.mesh.primitive_uv_sphere_add(
                size=self.base_size,
                location=self.pos,
                segments=self.resolution,
                ring_count=self.resolution//2)
        self.blend_obj = bpy.context.active_object
        vertices = self.blend_obj.data.vertices
        max_z = max(map(lambda co: co.co[2], vertices))
        min_z = min(map(lambda co: co.co[2], vertices))
        for i in range(len(vertices)):
            r, theta, phi = _to_spherical(vertices[i].co)
            if random.random() > (1.0 - self.peak_probability) and \
                    vertices[i].co.z <= (max_z - self.margin) and \
                    vertices[i].co.z >= (min_z + self.margin):
                r += random.randint(-self.max_peak_height, self.max_peak_height)
            new_co = _to_xyz(Vector((r, theta, phi)))
            vertices[i].co = new_co

        # Smooth it up
        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].factor = self.smooth_factor
        bpy.context.object.modifiers["Smooth"].iterations = self.smooth_steps
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

        self.blend_obj.name = self.name

    @property
    def bound_box(self):
        '''Minimum and maximum of bounding box'''
        bbox = self.blend_obj.bound_box
        coords = [v[:] for v in bbox]
        return Vector(coords[0]), Vector(coords[6])
