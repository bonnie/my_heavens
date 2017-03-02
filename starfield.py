"""Starfield object and methods for calculating stars and constellation display"""

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime

from model import db, Star, Constellation
from display_constants import STARFIELD_RADIUS

# optional debugging output
DEBUG = False


class Starfield(object):
    """Class for calculating stars and constellation display"""

    def __init__(self, lat, lng, utctime=None, display_radius=STARFIELD_RADIUS):
        """Initialize Starfield object. 

        * lat is latitude in degrees (positive / negative)
        * lng is longitude in degrees (positive / negative)
        * utctime, if provided is datetime. If not provided, will default to now
        * display_radius is display radius. Specifiable for ease of testing. 
        """

        self.utctime = utctime or datetime.utcnow()
        self.display_radius = display_radius

        # change lat and lng to radians
        self.lat = lat
        self.lng = lng
        self.update_latlng_rads()


    def __repr__(self):
        """Helpful representation when printed."""

        return '< Starfield lat={}, lng={}, utctime={} >'.format(self.lat,
                                                                 self.lng,
                                                                 self.utctime)


    def update_latlng_rads(self):
        """given lat and long in degrees, return in radians

        * self.lat is latitude in degrees (positive / negative)
        * self.lng is longitude in degrees (positive / negative)
        """

        # update lat/lng to this format to make sidereal happy
        # '37.7749dN'  (d for degrees, N for north)
        # '122.4194dW' (d for degrees, W for west)

        lat = str(self.lat)
        lng = str(self.lng)

        lat = lat[1:] + 'dS' if lat[0] == '-' else lat + 'dN'
        lng = lng[1:] + 'dW' if lng[0] == '-' else lng + 'dE'

        # update degrees to radians
        self.lat = parseLat(lat)
        self.lng = parseLon(lng)


    def pol2cart(self, rho, phi):
        """translate between polar coords and svg-style cartesian coords

        in svg, the origin is in the upper left and y is positive going down

        adapted from 
        http://stackoverflow.com/questions/20924085/python-conversion-between-coordinates"""

        # rotate so that north (phi = 0) is up, not to the right
        rotated_phi = phi + math.pi / 2

        x_from_center = rho * np.cos(rotated_phi)
        y_from_center = rho * np.sin(rotated_phi)

        # transform for the wacky svg axes
        x = x_from_center + self.display_radius
        y = self.display_radius - y_from_center

        return (x, y)

