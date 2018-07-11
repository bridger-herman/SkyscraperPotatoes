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

import importlib

class Mapper:
    def __init__(self):
        self.a, self.b = None, None
        self.have_coefficients = False

    def get_coefficients(self):
        fmin, fmax = self.get_bounds()
        desired_min, desired_max = self.output_range
        self.a = (desired_max - desired_min)/(fmax - fmin)
        self.b = desired_max - self.a*fmax
        self.have_coefficients = True
        print(0, "Linear Mapping Coefficients: a={:.6f} b={:.6f}".format(self.a, self.b))
        return self.a, self.b

    # To be overridden
    def get_bounds(self):
        return None

    # To be overridden
    def map(self):
        return None

class LinearMapper(Mapper):
    def __init__(self, input_range, output_range):
        super().__init__()
        self.input_range = input_range
        self.output_range = output_range

    def get_bounds(self):
        return self.input_range

    def map(self, value, *args):
        if not self.have_coefficients:
            self.get_coefficients()
        return self.a*value + self.b

class LinearMapper3D(Mapper):
    def __init__(self, x_dom, y_dom, z_dom, fn, output_range, step=0.5, num_bins=None):
        super().__init__()
        self.x_dom = x_dom
        self.y_dom = y_dom
        self.z_dom = z_dom
        self.fn = fn
        self.output_range = output_range
        self.step = step
        self.bounds = None
        self.num_bins = num_bins
        self.bins = {}

    def get_bins(self):
        if self.num_bins != None:
            fmin, fmax = self.bounds
            bucket_size = (fmax - fmin)/self.num_bins
            n = fmin
            while n <= fmax:
                lower = n
                upper = n + bucket_size
                # self.bins[(lower, upper)] = lower
                # self.bins[(lower, upper)] = upper
                self.bins[(lower, upper)] = (upper + lower)/2
                n += bucket_size

    def get_bounds(self):
        fmax = float('-inf')
        fmin = float('inf')
        xi = self.x_dom[0]
        while xi <= self.x_dom[1]:
            yi = self.y_dom[0]
            while yi <= self.y_dom[1]:
                zi = self.z_dom[0]
                while zi <= self.z_dom[1]:
                    fn_output = self.fn(xi, yi, zi)
                    if fn_output > fmax:
                        fmax = fn_output
                    if fn_output < fmin:
                        fmin = fn_output
                    zi += self.step
                yi += self.step
            xi += self.step
        self.bounds = (fmin, fmax)
        return fmin, fmax

    def map(self, x, y, z, *args):
        if not self.have_coefficients:
            self.get_coefficients()
            self.get_bins()
        value = self.fn(x, y, z)
        if self.num_bins != None:
            for bmin, bmax in self.bins:
                if bmin <= value and value <= bmax:
                    value = self.bins[(bmin, bmax)]
                    break
        return self.a*value + self.b
