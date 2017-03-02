"""Starfield object and methods for calculating stars and constellation display"""

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime

from model import db, Star, Constellation
from display_constants import STARFIELD_RADIUS

# optional debugging output
DEBUG = False


class StarField(object):
    """Class for calculating stars and constellation display"""

    def __init__(self, lat, lng, utctime=None, display_radius=STARFIELD_RADIUS,
                 max_mag=5):
        """Initialize Starfield object. 

        * lat is latitude in degrees (positive / negative)
        * lng is longitude in degrees (positive / negative)
        * utctime, if provided is datetime. If not provided, will default to now
        * display_radius is display radius. Specifiable for ease of testing. 
        * max_mag is the maximum magnitude to display for this starfield (to
          eliminate dim stars)
        """

        self.utctime = utctime or datetime.utcnow()
        self.display_radius = display_radius
        self.max_mag = max_mag

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


    def get_display_coords(self, ra, dec, calculate_invisible=False):
        """Return display x and y (for this starfield) for a particular ra and dec

        * ra and dec are Decimal objects (in radians)
        * if "calculate_invisible" is True, calculate coords for points beyond 
            the horizon; otherwise return without calculating 
            (return None for x and y, and False for visible)

        return value: dict with these keys: 

            x (float or None)
            y (float or None)
            visible (boolean saying whether the point was below the horizon)

        """

        # assume ra and dec come in as Decimal objects
        coords = RADec(float(ra), float(dec))

        ha = coords.hourAngle(self.utctime, self.lng)
        altaz = coords.altAz(ha, self.lat)

        # is this point below the horizon? 
        visible = altaz.alt > 0

        # for points below the horizon
        if not (visible or calculate_invisible):
            # discard this point
            return {'x': None, 'y': None, 'visible': False}

        # convert alt and az into x and y, considering the size of our star field

        # translate alt and az into polar coords
        rho = (math.pi/2 - altaz.alt) * self.display_radius / (math.pi / 2)
        phi = altaz.az
        x, y = self.pol2cart(rho, phi)
        
        return {'x': x, 'y': y, 'visible': visible}


    def get_star_data(self):
        """return list of star dicts in for the starfield

        star dict keys: 
            "x": display x coord for star
            "y": display y coord for star
            "magnitude": magnitude of star
            "color": color corresponding to star's spectral class
            "name": star's name

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

            if star.magnitude > self.max_mag: 
                # skip stars that are too dim
                continue

            # convert RA and dec into alt and az
            p = self.get_display_coords(star.ra, star.dec)

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