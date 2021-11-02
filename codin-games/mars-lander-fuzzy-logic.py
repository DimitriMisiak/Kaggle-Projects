import sys
import math as m
import numpy as np

# Save the Planet.
# Use less Fossil Fuel.

surface_n = int(input())  # the number of points used to draw the surface of Mars.

surface_points = []
for i in range(surface_n):
    # land_x: X coordinate of a surface point. (0 to 6999)
    # land_y: Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
    land_x, land_y = [int(j) for j in input().split()]
    surface_points.append([land_x, land_y])
surface_points = np.array(surface_points)

# searching for flat landing zone
surface_y_diff = surface_points[:-1, 1] - surface_points[1:, 1]
flat_surface_left_points_idxs = np.nonzero(surface_y_diff == 0)[0]

landing_sites = []
for i in flat_surface_left_points_idxs:
    site_dict = {}
    site_dict['height'] = surface_points[i, 1]
    site_dict['x_inf'] = surface_points[i, 0]
    site_dict['x_sup'] = surface_points[i+1, 0]
    landing_sites.append(site_dict)

print(landing_sites, file=sys.stderr, flush=True)

# selecting landing zone
landing_site = landing_sites[0]

x_inf = landing_site['x_inf']
x_sup = landing_site['x_sup']
y_goal = landing_site['height']

x_goal = (x_inf + x_sup)/2
# x_delta = x_goal - x_inf

def delta_x(x):
    if x < x_inf:
        return x_inf - x
    elif x > x_sup:
        return x_sup - x
    else:
        return 0

hs_coeff = 1
hs_goal = 1

speed_levels = {
    "very fast":200,
    "fast":120,
    "medium":60,
    "low":30,
    "stop":0,
}

def BasisFunction(left, center, right):
    def basis_function(x):
        if (x < left) or (x > right):
            return 0
        if left <= x < center:
            return (x - left) / (center - left)
        if center <= x <= right:
            return (right - x) / (right - center)  
    return basis_function

def LeftBasisFunction(center, right):
    def basis_function(x):
        if (x > right):
            return 0
        if center <= x <= right:
            return (right - x) / (right - center) 
        if x < center:
            return 1
    return basis_function

def RightBasisFunction(left, center):
    def basis_function(x):
        if (x < left):
            return 0
        if left <= x <= center:
            return (x - left) / (center - left)
        if x > center:
            return 1
    return basis_function

class FuzzyScale():

    def __init__(self, labels, values):
        assert len(labels) == len(values)
        self.labels = labels
        self.values = values

        self._basis_functions = []
        for i in range(len(values)):
            if i == 0:
                basis_function = LeftBasisFunction(
                    self.values[i], self.values[i+1]
                )
            elif i == len(values) - 1:
                basis_function = RightBasisFunction(
                    self.values[i-1], self.values[i]
                )
            else:
                basis_function = BasisFunction(
                    self.values[i-1], self.values[i], self.values[i+1]
                )

            self._basis_functions.append(basis_function)

    def make_fuzzy(self, x):
        fuzzy_values = [f(x) for f in self._basis_functions]
        return fuzzy_values
    
fuzzy_x = FuzzyScale(
    ["V.left", "left", "center", "right", "V.right"],
    [0, x_inf, x_goal, x_sup, 7000]
)

fuzzy_y = FuzzyScale(
    ["contact", "near", "far", "V.far"],
    [y_goal+50, y_goal + 500, y_goal + 1000, y_goal + 2000]
)

fuzzy_vs = FuzzyScale(
    ["V.fast", "fast", "medium", "target", "ascending"],
    [-150, -100, -60, -30, 0]
)


rotate_levels = [-90, -20, 0, 20, 90]

power_levels = [0, 1, 2, 3, 4]

# successful landing:
# sol plat: x_inf < x < x_sup
# vertical position: angle = 0
# slow vertical speed: abs(vs) <= 40
# slow horizontal speed: abs(hs) <= 20



# game loop
while True:
    # hs: the horizontal speed (in m/s), can be negative.
    # vs: the vertical speed (in m/s), can be negative.
    # f: the quantity of remaining fuel in liters.
    # r: the rotation angle in degrees (-90 to 90).
    # p: the thrust power (0 to 4).
    x, y, hs, vs, fuel, angle, power = [int(i) for i in input().split()]

    print(x, y, hs, vs, fuel, angle, power, file=sys.stderr, flush=True)

    x_levels = fuzzy_x.make_fuzzy(x)
    y_levels = fuzzy_y.make_fuzzy(y)
    vs_levels = fuzzy_vs.make_fuzzy(vs)

    print(fuzzy_x.labels, file=sys.stderr, flush=True)
    print(x_levels, file=sys.stderr, flush=True)

    print(fuzzy_y.labels, file=sys.stderr, flush=True)
    print(y_levels, file=sys.stderr, flush=True)

    print(fuzzy_vs.labels, file=sys.stderr, flush=True)
    print(vs_levels, file=sys.stderr, flush=True)

    try:
        rotate = m.degrees(m.atan(-hs/vs))
        print("adjusting angle to ", rotate, file=sys.stderr, flush=True)

        rotate_correction = sum([a*b for a,b in zip(
            x_levels, rotate_levels
        )])

        print("rotate_correction ", rotate_correction, file=sys.stderr, flush=True)
        # rotate *= (1 - vs_levels[-1])
        rotate += rotate_correction
        rotate *=  (1 - y_levels[0])

    except:
        rotate = angle
        print("keeping angle", file=sys.stderr, flush=True)

    if abs(rotate) > 90:
        rotate *= 90/abs(rotate)

    rotate = int(rotate)

    power = sum([a*b for a,b in zip(
            vs_levels, [1, 1, 3, 4, 2]
    )])

    power = int(power)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # R P. R is the desired rotation angle. P is the desired thrust power.
    print(f"{rotate} {power}")
