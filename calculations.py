"""functions for deciding what stars to show"""

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime

from model import connect_to_db, Star
from display_constants import STARFIELD_RADIUS


def pol2cart(rho, phi):
    """ from http://stackoverflow.com/questions/20924085/python-conversion-between-coordinates"""

    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)


def get_user_star_coords(lat, lng, utctime):
    """return json of stars in for the location and current time, in user coords

    lat and lng are in degrees in this format: 
    '37.7749dN'  (d for degrees, N for north)
    '122.4194dW' (d for degrees, W for west)


    utctime is a datetime obj, in utc

    sample output: 

    [ {"x": 15, "y": 130, "magnitude": 1.7, "color": }
        ...
    ]
    """


    # degrees to radians
    longitude_in_radians = parseLon(lng)
    latitude_in_radians = parseLat(lat)

    # get list of stars
    db_stars = Star.query.all()

    star_field = []


    for star in db_stars:

        # convert RA and dec into alt and az
        coords = RADec(float(star.ra), float(star.dec))
        ha = coords.hourAngle(utctime, longitude_in_radians)
        altaz = coords.altAz(ha, latitude_in_radians)

        # convert alt and az into x and y, considering the size of our star field

        # translate alt and az into polar coords
        rho = (math.pi/2 - altaz.alt) * STARFIELD_RADIUS / (math.pi * 2)
        phi = altaz.az

        x, y = pol2cart(rho, phi)

        # add it to the list in a neat little package
        #
        # cast magnitude and color to floats, as they come back as decimals, 
        # to which json objects
        star_field.append({'x': x, 
                           'y': y, 
                           'magnitude': float(star.magnitude), 
                           # 'color': float(star.color_index) # do color later. It's hard. 
                           })

        # print x
        # print y
        # print star.magnitude
        # print star.color_index

    return star_field