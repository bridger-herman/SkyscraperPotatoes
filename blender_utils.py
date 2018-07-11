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

import sys
import random
from mathutils import Vector, Matrix

sys.path.append('.')

# Converts a quad into two triangles
def to_tri(points):
    return [[points[0], points[1], points[3]], [points[1], points[2], points[3]]]

# Finds the centroid of a set of points
# :points: (list of 3-tuples)
def centroid(points):
    sum_x, sum_y, sum_z = 0, 0, 0
    for x, y, z in points:
        sum_x += x
        sum_y += y
        sum_z += z
    return (sum_x/len(points), sum_y/len(points), sum_z/len(points))

# Finds the absolute maxima and minima of a set of points
# :points: (list of 3-tuples)
def extrema(points):
    max_x, max_y, max_z = points[0]
    min_x, min_y, min_z = points[0]
    for p in points:
        max_x = max_x if max_x > p[0] else p[0]
        max_y = max_y if max_y > p[1] else p[1]
        max_z = max_z if max_z > p[2] else p[2]
        min_x = min_x if min_x < p[0] else p[0]
        min_y = min_y if min_y < p[1] else p[1]
        min_z = min_z if min_z < p[2] else p[2]
    return ((min_x, min_y, min_z), (max_x, max_y, max_z))

# Determine if a point is within the "radius" of another point
# :p1: (3-tuple)
# :p2: (3-tuple)
# :r: float
def within_radius(p1, p2, r):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    # Bounding box within
    if x1 < (x2 + r) and x1 > (x2 - r) and \
        y1 < (y2 + r) and y1 > (y2 - r) and \
        z1 < (z2 + r) and z1 > (z2 - r):
        return (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2 < r**2
    else:
        return False

# Determine if a point is within the "radius" of another point
# :p1: (3-tuple)
# :p2: (3-tuple)
# :r: (float) "radius" of the cube
def within_cube(p1, p2, r):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return x1 < (x2 + r) and x1 > (x2 - r) and \
        y1 < (y2 + r) and y1 > (y2 - r) and \
        z1 < (z2 + r) and z1 > (z2 - r)

# Determine if a point is within the "radius" of another point
# :p1: (3-tuple)
# :p2: (3-tuple)
# :bounds: (3-tuple) 'radius' for x, y, z coordinates
def within_box(p1, p2, bounds):
    xb, yb, zb = bounds
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return x1 < (x2 + xb) and x1 > (x2 - xb) and \
            y1 < (y2 + yb) and y1 > (y2 - yb) and \
            z1 < (z2 + zb) and z1 > (z2 - zb)

# Determine if a point is within a triangle
# Uses "half-space" test
# :a: .. :n: (Vector)
def within_triangle(a, b, c, p, n):
    a_gt0 = ((b - a).cross(p - a)).dot(n) > 0
    b_gt0 = ((c - b).cross(p - b)).dot(n) > 0
    c_gt0 = ((a - c).cross(p - c)).dot(n) > 0
    return all((a_gt0, b_gt0, c_gt0)) or all((not a_gt0, not b_gt0, not c_gt0))

# Returns a random point, on the "face" of the given points
# Assumes they are actually in a plane of some sort
# :points: (list of 3-tuples) Points that make up the polygon
# :normal: (3-tuple) Normal vector of the polygon
# :extrema: (duple of 3-tuples) Extrema of the points (returned by fn extrema)
# :margin: (float) How close to the edge can we place the point?
def random_inside(points, normal, extrema):
    (min_x, min_y, min_z), (max_x, max_y, max_z) = extrema
    # NOTE: assumes the plane is not vertical
    if min_x == max_x or min_y == max_y:
        return None
    x, y, p = 0, 0, True
    x, y = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
    # Find the z coordinate that is in the plane
    x0, y0, z0 = points[0]
    a, b, c = normal
    d = a * x0 + b * y0 + c * z0
    z = (d - b * y - a * x) / c
    if z > max_z or z < min_z:
        return None
    return (x, y, z)

def rotate_obj(obj, normal, up=Vector((0, 0, 1))):
    rotation_axis = up.cross(normal.normalized())
    rotation_angle = normal.angle(up)
    obj.rotation_mode='AXIS_ANGLE'
    obj.rotation_axis_angle = (rotation_angle,) + tuple(rotation_axis)
    print(0, "rotation", *obj.rotation_axis_angle)

def rotate_obj_gradient(obj, normal, gradient):
    z = normal.normalized()
    x_temp = gradient.normalized()
    y = x_temp.cross(z)
    x = y.cross(z)

    m = Matrix((
        (x[0], y[0], z[0], 0),
        (x[1], y[1], z[1], 0),
        (x[2], y[2], z[2], 0),
        (  0 ,   0 ,   0 , 1),
    ))

    scale = obj.scale

    obj.matrix_world *= m

    # Re-adjust the scale
    obj.scale = Vector((1, 1, 1))

def nearest_vertex(vertices, coord):
    min_index = 0
    min_dist = (vertices[0].co - coord).length
    for i, v in enumerate(vertices[1:]):
        dist = (v.co - coord).length
        if dist < min_dist:
            min_dist = dist
            min_index = i
    return min_index, min_dist

def find_vertex_neighbor_indices(edges, vertex_index):
    return list(
            map(lambda ed: ed.vertices[0] if vertex_index != ed.vertices[0] \
                else ed.vertices[1],
            filter(lambda e: vertex_index in e.vertices, edges))
    )

def gradient_at_vertex(edges, vertices, vert_index):
    """Take the gradient at a given vertex"""
    selected_vert = vertices[vert_index]

    downhill_sum = Vector((0, 0, 0))
    neighbor_indices = find_vertex_neighbor_indices(edges, selected_vert.index)

    dots = [(index, 1 - selected_vert.normal.dot(vertices[index].normal)) \
            for index in neighbor_indices]

    _, max_dot = max(dots, key=lambda t: t[1])
    _, min_dot = min(dots, key=lambda t: t[1])

    denom = max_dot - min_dot

    interpolated_dots = list(map(lambda l: \
            (l[0], (l[1] - min_dot)/denom) if abs(denom) > 0.000001 else
            (l[0], 1), dots))

    suma = Vector((0, 0, 0))
    for index, weight in interpolated_dots:
        suma += weight * (vertices[index].co - selected_vert.co).normalized()

    weighted_avg_co = suma / len(interpolated_dots)

    return weighted_avg_co


def gradient_at_vertex_2(edges, vertices, vert_index):
    """Take the average gradient of every vertex in the 2-ring"""
    selected_vert = vertices[vert_index]

    downhill_sum = Vector((0, 0, 0))
    neighbor_indices = find_vertex_neighbor_indices(edges,
            selected_vert.index)

    max_dist = max(map(lambda i: (vertices[i].co -
            vertices[vert_index].co).length, neighbor_indices))

    for index in neighbor_indices:
        n2_indices = find_vertex_neighbor_indices(edges, index)

        # Calculate gradient for this neighbor and weight it with distance
        grad = gradient_at_vertex(edges, vertices, index)
        downhill_sum += (max_dist - (vertices[index].co -
                vertices[vert_index].co).length) * grad

        max_dist2 = max(map(lambda i: (vertices[i].co -
                vertices[vert_index].co).length, n2_indices))

        # Compute the second ring gradients and weight them
        sub_sum = Vector((0, 0, 0))
        for n2_index in n2_indices:
            grad2 = gradient_at_vertex(edges, vertices, n2_index)
            sub_sum += (max_dist2 - (vertices[n2_index].co -
                    vertices[vert_index].co).length) * grad2
        downhill_sum += sub_sum/len(n2_indices)

    return ((downhill_sum/len(neighbor_indices)) + \
            gradient_at_vertex(edges, vertices, vert_index))/2
