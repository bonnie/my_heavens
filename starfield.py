"""Starfield object and methods for calculating stars and constellation display"""

import ephem
from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
import numpy as np
from datetime import datetime
import pytz
import requests

from model import db, Star, Constellation
from time_functions import to_utc
from colors import PLANET_COLORS_BY_NAME

# to determine which non-star objects to find
NON_STARS = [ ephem.Sun, ephem.Moon, ephem.Mercury, ephem.Venus, ephem.Mars, 
              ephem.Jupiter, ephem.Saturn, ephem.Neptune, ephem.Uranus ]

# how datetime comes in from bootstrap. For example "2017-01-01T01:00"
BOOTSTRAP_DTIME_FORMAT = '%Y-%m-%dT%H:%M'

# how ephem expects / gives dates
EPHEM_DTIME_FORMAT = '%Y/%-m/%-d %H:%M:%S'

# for getting time zones
GOOGLE_TZ_URL = 'https://maps.googleapis.com/maps/api/timezone/json'

# optional debugging output
DEBUG = False


class StarField(object):
    """Class for calculating stars and constellation display"""

    def __init__(self, lat, lng, display_radius, localtime_string=None, max_mag=5):
        """Initialize Starfield object. 

        * lat is latitude in degrees (positive / negative)
        * lng is longitude in degrees (positive / negative)
        * localtime_string, if provided, is string in BOOTSTRAP_DTIME_FORMAT. 
            If not provided, will default to now
        * display_radius is display radius. Specifiable for ease of testing. 
        * max_mag is the maximum magnitude to display for this starfield (to
          eliminate dim stars)
        """

        self.display_radius = display_radius
        self.max_mag = max_mag

        # change lat and lng to radians, but store the degrees for google tz and ephem
        self.lat_deg = lat
        self.lng_deg = lng
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

        lat = str(self.lat_deg)
        lng = str(self.lng_deg)

        lat = lat[1:] + 'dS' if lat[0] == '-' else lat + 'dN'
        lng = lng[1:] + 'dW' if lng[0] == '-' else lng + 'dE'

        # update degrees to radians
        self.lat = parseLat(lat)
        self.lng = parseLon(lng)


    def get_timezone(self, localtime):
        """return the timezone based on the lat/lng and desired time.

        localtime is a naive (non-timezone-aware) datetime object.

        Use google timezone api to get timezone."""

        # bury this here to avoid circular imports
        from server import GOOGLE_KEY

        # get timestamp / unixtime from the local time
        localtime_tstamp = localtime.strftime('%s')

        params = { 'key': GOOGLE_KEY,
                   'location': '{},{}'.format(self.lat_deg, self.lng_deg),
                   'timestamp': localtime_tstamp }

        response = requests.get(GOOGLE_TZ_URL, params)
        tz_data = response.json()

        if tz_data['status'] != 'OK':
            # TODO: make for better user experience here
            print 'ERROR! google didn\'t want to play: {}'.format(tz_data['status']) 
            return pytz.utc

        tzid = tz_data['timeZoneId']

        return pytz.timezone(tzid)


    def set_utc_time(self, localtime_string):
        """Sets self.utctime based on the local time and the lat/lng.

        * localtime_string is, well, a string
        """

        if not localtime_string:
            # no time like the present! 
            self.utctime = datetime.utcnow()

        else:
            
            # get localtime with no timezone        
            dtime_local = datetime.strptime(localtime_string, BOOTSTRAP_DTIME_FORMAT)

            # get time zone based on lat/lng 
            local_tz = self.get_timezone(dtime_local)

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


    def get_pixel_size_from_arcsec(self, size_in_arcsec):
        """Return pixel size for a given measurement in arcseconds."""

        size_in_degrees = size_in_arcsec / 3600
        size_in_pixels = self.display_radius * size_in_degrees / 90

        return size_in_pixels


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

            # names based on the constellation aren't interesting
            name = star.name
            if star.name and star.const_code and star.name[-3:].lower() == star.const_code.lower():
                name = None

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
                               'name': name
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


    def get_planet_data(self, eph, planet):
        """Return a dict of planet data for the ephem object and planet object.

        Returns None if planet is not visible for this starfield.

        Example planet dict: 
        {'name': 'Jupiter',
         'x': 117.34,
         'y': 489.13,
         'magnitude': -2.21,
         'color': '#ffffc8'
         'size': 0.002 } # size is in pixels
        """

        # using the ephemeris way of getting data for a planet for this date
        pla = planet(eph)

        # if it's too dim, don't return it
        if pla.mag > self.max_mag:
            return None

        # get coords for planet for this starfield
        pt = self.get_display_coords(pla.ra, pla.dec)

        if not pt['visible']: 
            return None

        # otherwise, gather data
        planet_data = {}

        planet_data['x'] = pt['x']
        planet_data['y'] = pt['y']
        planet_data['magnitude'] = pla.mag
        planet_data['name'] = pla.name
        planet_data['color'] = PLANET_COLORS_BY_NAME[pla.name]

        # translate size to pixels
        planet_data['size'] = self.get_pixel_size_from_arcsec(pla.size)

        return planet_data


    def get_planets(self):
        """Return a list of planet data dicts, transformed for d3.

        see get_planet_data docstring for description of planet data dict
        """

        # alert ephem of starfield properties
        stf_ephem = ephem.Observer()
        stf_ephem.lon = self.lng_deg
        stf_ephem.lat = self.lat_deg

        # ephem uses utctime
        stf_ephem.date = datetime.strftime(self.utctime, EPHEM_DTIME_FORMAT)

        planets = []

        for planet in NON_STARS:
            pdata = self.get_planet_data(stf_ephem, planet)
            if pdata:
                planets.append(pdata)

        return planets