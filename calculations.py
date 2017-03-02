"""functions for deciding what stars to show"""

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime

from model import Star
from display_constants import STARFIELD_RADIUS

# optional debugging output
DEBUG = False


def pol2cart(rho, phi, starfield_radius):
    """translate between polar coords and svg-style cartesian coords

    in svg, the origin is in the upper left and y is positive going down

    adapted from 
    http://stackoverflow.com/questions/20924085/python-conversion-between-coordinates"""

    # rotate so that north is up, not to the right
    rotated_phi = phi + math.pi / 2

    x_from_center = rho * np.cos(rotated_phi)
    y_from_center = rho * np.sin(rotated_phi)

    # transform for the wacky svg axes
    x = x_from_center + starfield_radius
    y = starfield_radius - y_from_center

    return(x, y)


def get_latlng_rads(lat, lng):
    """given lat and long in degrees, return in radians

    lat and lng are in this format: 
    '37.7749dN'  (d for degrees, N for north)
    '122.4194dW' (d for degrees, W for west)
    """

    # degrees to radians
    lat_in_radians = parseLat(lat)
    lng_in_radians = parseLon(lng)

    return lat_in_radians, lng_in_radians


def get_star_coords(lat, lng, utctime, ra, dec, starfield_radius, 
                    calculate_invisible=False):
    """reusable function to get x and y for a particular ra and dec

    * lat and lng are in radians
    * utctime is a datetime obj, in utc
    * ra and dec are Decimal objects (in radians)
    * if "calculate_invisible" is True, calculate coords for points beyond 
        the horizon; otherwise return without calculating (return None for x and
        y)

    return value: dict with these keys: 

        x (float)
        y (float)
        visible (boolean saying whether the point was below the horizon)

    """

    # assume ra and dec come in as Decimal objects
    coords = RADec(float(ra), float(dec))

    ha = coords.hourAngle(utctime, lng)
    altaz = coords.altAz(ha, lat)

    # is this point below the horizon? 
    visible = altaz.alt > 0

    # for points below the horizon
    if not (visible or calculate_invisible):
        # discard this point
        return {'x': None, 'y': None, 'visible': False}

    # convert alt and az into x and y, considering the size of our star field

    # translate alt and az into polar coords
    rho = (math.pi/2 - altaz.alt) * starfield_radius / (math.pi / 2)
    phi = altaz.az
    x, y = pol2cart(rho, phi, starfield_radius)
    
    return {'x': x, 'y': y, 'visible': visible}


def get_user_star_coords(lat, lng, utctime, max_mag, starfield_radius):
    """return json of stars in for the location and current time, in user coords

    * lat and lng are in radians
    * utctime is a datetime obj, in utc

    sample output: 

    [ {"x": 15, "y": 130, "magnitude": 1.7, "color": "#ffffff", "name": "alpha Ori"}
        ...
    ]
    """

    # get list of stars
    db_stars = Star.query.all()

    star_field = []

    if DEBUG: 
        print 'lat', lat
        print 'lng', lng
        print 'utctime = strptime("{}", "%Y-%m-%d %H-%M-%S.%f'.format(utctime)

    for star in db_stars:

        if star.magnitude > max_mag: 
            # skip stars that are too dim
            continue

        # convert RA and dec into alt and az
        p = get_star_coords(lat, lng, utctime, star.ra, star.dec, starfield_radius)

        # if the star is below the horizon, don't add it to the list
        if not p['visible']:
            continue

        # add it to the list in a neat little package
        #
        # cast magnitude to float, as it comes back as a Decimal obj: bad json
        star_field.append({'x': p['x'], 
                           'y': p['y'], 
                           'magnitude': float(star.magnitude), 
                           'color': star.color,
                           'name': star.name
                           })

    return star_field
