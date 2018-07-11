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
import importlib

# Other imports
# importlib is necessary because Blender caches copies of the scripts
sys.path.append(".")
import glyph_cube
importlib.reload(glyph_cube)
from glyph_cube import *

import mapper
importlib.reload(mapper)
from mapper import *

import potato
importlib.reload(potato)
from potato import *

import mesh_helpers
importlib.reload(mesh_helpers)
from mesh_helpers import *

def main():
    # Define the glyph sizes
    # Based on viewing angle at 25cm, from Li et al. 2010
    radius_range = (0.314, 2.5)
    height_range = (0.5, 3.0)
    length_range = (1, 3.5)
    length_range2 = (1, 3.5)

    p = Potato()
    p.generate()

    minm, maxm = p.bound_box

    # Use a simple scalar field to plot:
    f = lambda x, y, z: x
    bundle = [(minm.x, maxm.x), (minm.y, maxm.y), (minm.z, maxm.z), f]

    # 8 bins (from Li et al.)
    # Length-based glyphs, pointing perpendicular to gradient
    #  m = LinearMapper3D(*bundle, output_range=length_range, num_bins=8)
    #  g = LengthCubeGenerator(p.blend_obj, m.map)

    # Length-based glyphs, pointing perpendicular to gradient
    #  m = LinearMapper3D(*bundle, output_range=length_range2, num_bins=8)
    #  g = LengthCubeGenerator2(p.blend_obj, m.map)

    # Height based glyphs
    #  m = LinearMapper3D(*bundle, output_range=height_range, num_bins=8)
    #  g = HeightCubeGenerator(p.blend_obj, m.map)

    # Radius-based glyphs
    m = LinearMapper3D(*bundle, output_range=radius_range, num_bins=8)
    g = SizeCubeGenerator(p.blend_obj, m.map)

    # Distribute the points on the potato. This might take a while
    points = g.distribute_poisson()

    # Take the difference of the skyscrapers and the potato
    boolean_op(g.blend_obj, p.blend_obj, 'DIFFERENCE')

    # Do some magic to prevent Python from modifying the bounding box while
    # slicing the potato in half
    coords = p.bound_box
    bbox = tuple(coords[:])

    # Non-destructively slice both the potato and the glyphs in half
    slice_obj(p.blend_obj, True, op='INTERSECT', bound_box=bbox)
    slice_obj(g.blend_obj, True, op='DIFFERENCE', bound_box=bbox)

if __name__ == '__main__':
    main()
