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

        * lat is latitude in degrees (positive / negative)
        * lng is longitude in degrees (positive / negative)
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