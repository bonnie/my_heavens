"""functions for deciding what stars to show"""

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime

from model import connect_to_db, Star
from display_constants import STARFIELD_RADIUS

# optional debugging output
DEBUG = True


def pol2cart(rho, phi):
    """translate between polar coords and svg-style cartesian coords

    in svg, the origin is in the upper left and y is positive going down

    adapted from 
    http://stackoverflow.com/questions/20924085/python-conversion-between-coordinates"""

    x_from_center = rho * np.cos(phi)
    y_from_center = rho * np.sin(phi)

    # transform for the wacky svg axes
    x = x_from_center + STARFIELD_RADIUS
    y = STARFIELD_RADIUS - y_from_center

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


def get_star_coords(lat, lng, utctime, ra, dec):
    """reusable function to get x and y for a particular ra and dec

    * lat and lng are in radians
    * utctime is a datetime obj, in utc
    * ra and dec are Decimal objects

    """

    # assume ra and dec come in as Decimal objects
    coords = RADec(float(ra), float(dec))

    ha = coords.hourAngle(utctime, lng)
    altaz = coords.altAz(ha, lat)

    # discard stars below the horizon
    if altaz.alt < 0:
        return None, None


    # convert alt and az into x and y, considering the size of our star field

    # translate alt and az into polar coords
    rho = (math.pi/2 - altaz.alt) * STARFIELD_RADIUS / (math.pi)
    phi = altaz.az

    x, y = pol2cart(rho, phi)

    return x, y


def get_user_star_coords(lat, lng, utctime, max_mag):
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
        x, y = get_star_coords(lat, lng, utctime, star.ra, star.dec)

        # if the star is below the horizon, don't add it to the list
        if not x:
            continue

        # add it to the list in a neat little package
        #
        # cast magnitude to float, as it comes back as a Decimal obj: bad json
        star_field.append({'x': x, 
                           'y': y, 
                           'magnitude': float(star.magnitude), 
                           'color': star.color,
                           'name': star.name
                           })


        if DEBUG: 
            if star.const_code == 'LUP': 
                print "x: {}, y: {}, ra={}, dec={}".format(x, y, star.ra, star.dec)

    return star_field