"""Starfield object and methods for calculating stars and constellation display"""

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime
import pytz

from model import db, Star, Constellation
from time_functions import to_utc

# how datetime comes in from bootstrap. For example "2017-01-01T01:00"
BOOTSTRAP_DTIME_FORMAT = '%Y-%m-%dT%H:%M'

# optional debugging output
DEBUG = False


class StarField(object):
    """Class for calculating stars and constellation display"""

    def __init__(self, lat, lng, display_radius, localtime_string=None, max_mag=5):
        """Initialize Starfield object. 

        * lat is latitude in degrees (positive / negative)
        * lng is longitude in degrees (positive / negative)
        * utctime, if provided is datetime. If not provided, will default to now
        * display_radius is display radius. Specifiable for ease of testing. 
        * max_mag is the maximum magnitude to display for this starfield (to
          eliminate dim stars)
        """

        self.display_radius = display_radius
        self.max_mag = max_mag

        # change lat and lng to radians
        self.lat = lat
        self.lng = lng
        self.update_latlng_rads()

        # translate local time to utc if necessary
        if localtime_string == None:
            self.utctime = datetime.utcnow()
        else:
            self.set_utc_time(localtime_string)


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


    def set_utc_time(self, localtime_string):
        """Sets self.utctime based on the local time and the lat/lng.

        * localtime_string is, well, a string
        """

        if not localtime_string:
            # no time like the present! 
            self.utctime = datetime.utcnow()

        else:
            
            # bury this here to avoid circular imports
            from server import GOOGLE_KEY

            # for now... 
            # https://developers.google.com/maps/documentation/timezone/intro
            local_tz = pytz.timezone('US/Pacific')

            # translate dtime string into datetime object
            # automatically in utc based on local server time

            # get localtime with no timezone        
            dtime_local = datetime.strptime(localtime_string, BOOTSTRAP_DTIME_FORMAT)

            # give it a time zone
            local_tz.localize(dtime_local)

            # translate to utc
            self.utctime = to_utc(local_tz, dtime_local)


    def pol2cart(self, rho, phi):
        """Translate between polar coords and svg-style cartesian coords.

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


    def get_stars(self):
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

    def get_const_line_groups(self, const):
        """Return a list of constellation line group data for input constellation

        * const is a Constellation instance

        Returns a tuple with two items: 

        * boolean of whether there were any visible lines at all
        * list of lists; each sublist contains dicts with 'x' and 'y' keys, 
        representing an independent line for this constellation. Coordinates are
        in x and y format based on the starfield's lat, lng, and the time

        """

        # track whether any points are above the horizon
        visible = False

        line_groups = []
        for grp in const.line_groups:
            grp_verts = []
            for vert in grp.constline_vertices:
                p = self.get_display_coords(vert.star.ra, vert.star.dec, 
                                       calculate_invisible=True)
                grp_verts.append({'x': p['x'], 'y': p['y']})

                if p['visible']:
                    visible = True

            line_groups.append(grp_verts)

        return visible, line_groups


    def get_const_bound_verts(self, const):
        """Return a dictionary of constellation data, transformed for d3

        * const is a Constellation instance

        returned list has this format: 

        * each element is a dict with 'x' and 'y' keys
        * Coordinates for boundary vertices are in x and y format based on the 
        starfield's lat, lng, and the time.
        """

        # collect the boundaries
        bound_verts = []
        for vert in const.bound_vertices:
            p = self.get_display_coords(vert.ra, vert.dec, calculate_invisible=True)
            bound_verts.append({'x': p['x'], 'y': p['y']})

        # add the final boundary point to close the boundary loop
        if bound_verts:
            bound_verts.append(bound_verts[0])

        return bound_verts


    def get_const_data(self, const):
        """Return a dictionary of constellation data, transformed for d3

        * const is a Constellation instance

        Coordinates for boundary vertices and constellation lines are in 
        x and y format based on the user's lat, lng, and the time

        returned dict has this format: 

        'code': <string>
        'name': <string>
        'bound_verts': <list of dicts with 'x' and 'y' keys>
        'line_groups': <list of lists of dicts with 'x' and 'y' keys>

        for the line_groups list, each sub-list represents an independent line
        for this constellation (see get_const_line_groups).
        """

        # temporary dict to store data for this constellation
        c = {}

        c['code'] = const.const_code
        c['name'] = const.name

        # get the constellation lines
        visible, line_groups = self.get_const_line_groups(const)

        # if there are no visible constellation lines, scrap this constellation
        if not visible: 
            return None

        c['line_groups'] = line_groups
        c['bound_verts'] = self.get_const_bound_verts(const)

        return c    


    def get_consts(self):
        """Return a list of constellation data dicts, transformed for d3.

        Returns a list of dicts of constellation data.
        See docstring for get_const_data for details on constellation dicts.
        """

        visible_consts = []

        # do joinedloads to make the data collection faster
        query = db.session.query(Constellation)
        const_joins = query.options(
                            db.joinedload("bound_vertices"),
                            db.joinedload("line_groups"))

        consts = const_joins.all()

        for const in consts:

            if DEBUG:
                print "\nlooking at constellation {}".format(const.name)

            const_data = self.get_const_data(const)
            if const_data: 
                visible_consts.append(const_data)


        return visible_consts
