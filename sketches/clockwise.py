# be able to import from parent dir
import sys
sys.path.append('..')

from model import Constellation


def is_d3_compatible(const):
    """given a constellation, determine whether it is clockwise"""

    points = const.bound_vertices

    # float-ify decimals so calculations will work
    float_points = [(float(p.ra), float(p.dec)) for p in points]

    # from http://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order

    # keep a running sum
    point_sum = 0

    # since I've already duplicated the last point from the first point, the
    # last comparison will be for the second-to-last point
    for i in range(len(float_points) - 1):
        pt = float_points[1]
        next_pt = float_points[i + 1]

        point_sum += (next_pt[0] - pt[0]) * (next_pt[1] - pt[1])


    # southern constellations actually need to be anti-clockwise to work with d3 polygon paths
    southern = all([dec < 0 for ra, dec in float_points])

    if southern:
        compat = point_sum < 0
    else:
        compat = point_sum > 0

    return compat


def evaluate_compatibility_of_constellations():
    """Print each constellation and whether it is clockwise or anti-clockswise"""

    constellations = Constellation.query.all()

    for const in constellations:
        print "\t{}: {}\n".format(const.name, is_d3_compatible(const))


if __name__ == "__main__":

    from model import connect_to_db
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)

    evaluate_compatibility_of_constellations()
