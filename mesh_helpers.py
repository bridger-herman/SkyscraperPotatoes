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
from mathutils import Vector
import math

def boolean_op(obj1, obj2, op, delete_obs=(False, False)):
    '''Perform a boolean modifier on 2 objects
        Common operations include:
            INTERSECT
            DIFFERENCE
    '''
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj1
    obj1.select = True
    name1 = str(obj1.name)
    name2 = str(obj2.name)
    print("Performing {} of {} and {}".format(op, name1, name2))
    bpy.ops.object.modifier_add(type='BOOLEAN')
    try:
        bpy.context.object.modifiers["Boolean"].solver = 'CARVE'
    except AttributeError:
        print('This version of Blender doesn\'t support changing solver')
    bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[name2]
    bpy.context.object.modifiers["Boolean"].operation = op
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
    bpy.ops.object.select_all(action='DESELECT')
    if delete_obs[0]:
        obj1.select = True
    elif delete_obs[1]:
        obj2.select = True
    if any(delete_obs):
        bpy.ops.object.delete(use_global=False)
    print("Finished\n")

def slice_obj(obj1, move=False, op='INTERSECT', destructive=False,
        bound_box=None, cutoff_buffer=0.01):
    '''Slice an object along the xy-plane
        INTERSECT for contiguous objects
        DIFFERENCE for disjoint objects
    '''
    print('Splitting object...')
    bpy.context.scene.objects.active = obj1
    obj1.select = True
    if not destructive:
        bpy.ops.object.duplicate()

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.duplicate()
    obj2 = bpy.context.active_object

    if bound_box == None:
        bbox = obj1.bound_box
        coords = [v[:] for v in bbox]
        minm, maxm = Vector(coords[0]), Vector(coords[6])
    else:
        minm, maxm = Vector(bound_box[0]), Vector(bound_box[1])

    bpy.ops.mesh.primitive_plane_add()
    ground = bpy.context.active_object
    ground.scale *= (maxm - minm).length / 1.9

    # Intersect the object with ground plane (bottom half)
    boolean_op(obj1, ground, op)
    select_all(obj1, False)
    select_fn(obj1, lambda x, y, z: z > cutoff_buffer)
    delete_verts(obj1)

    # Intersect the object with ground plane (top half)
    ground.rotation_euler[1] = math.radians(180)
    boolean_op(obj2, ground, op)
    select_all(obj2, False)
    select_fn(obj2, lambda x, y, z: z < -cutoff_buffer)
    delete_verts(obj2)

    bpy.ops.object.select_all(action='DESELECT')
    ground.select = True
    bpy.ops.object.delete(use_global=False)

    # Move the bottom half next to the top half
    if move:
        obj1.location[0] += 2.3 * maxm.x
        obj1.rotation_euler[1] = math.radians(180)

    print('Finished')
    return obj1, obj2

def select_all(obj, select=False):
    '''Select/deselect vertices/edges/polygons'''
    for i in range(len(obj.data.vertices)):
        obj.data.vertices[i].select = select
    for i in range(len(obj.data.polygons)):
        obj.data.polygons[i].select = select
    for i in range(len(obj.data.edges)):
        obj.data.edges[i].select = select

def select_fn(obj, f, select=True):
    '''Select vertices based on a function of the vertex coordinates'''
    for v in obj.data.vertices:
        x, y, z = v.co
        if f(x, y, z):
            v.select = select

def delete_verts(obj):
    obj.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
