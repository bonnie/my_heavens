"""Starfield object and methods for calculating stars and constellation display"""

import ephem
from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
import math
from datetime import datetime
import pytz
from tzwhere import tzwhere

from model import db, Star, Constellation
from time_functions import to_utc
from colors import PLANET_COLORS_BY_NAME

# it takes some time to initialize this, so do it once when the file loads
TZW = tzwhere.tzwhere()

# to determine which non-star objects to find
NON_STARS = [ ephem.Sun, ephem.Mercury, ephem.Venus, ephem.Mars, 
              ephem.Jupiter, ephem.Saturn, ephem.Neptune, ephem.Uranus ]

# how datetime comes in from bootstrap. For example "2017-01-01T01:00"
BOOTSTRAP_DTIME_FORMAT = '%Y-%m-%dT%H:%M'

# how ephem expects / gives dates
EPHEM_DTIME_FORMAT = '%Y/%-m/%-d %H:%M:%S'

# for getting time zones
GOOGLE_TZ_URL = 'https://maps.googleapis.com/maps/api/timezone/json'

# optional debugging output
DEBUG = False

def rad_to_deg(angle):
    """Return angle (in radians) translated into degrees"""

    return angle / math.pi * 180


class StarField(object):
    """Class for calculating stars and constellation display"""

    def __init__(self, lat, lng, localtime_string=None, max_mag=5):
        """Initialize Starfield object. 

        * lat is latitude in degrees (positive / negative)
        * lng is longitude in degrees (positive / negative)
        * localtime_string, if provided, is string in BOOTSTRAP_DTIME_FORMAT. 
            If not provided, will default to now
        * max_mag is the maximum magnitude to display for this starfield (to
          eliminate dim stars)
        """

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

        # make an ephemeris for planetary data
        self.make_ephem()


    def __repr__(self):
        """Helpful representation when printed."""

        return '< Starfield lat={}, lng={}, utctime={} >'.format(self.lat_deg,
                                                                 self.lng_deg,
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


    def make_ephem(self):
        """Generate an ephemeris for pyEphem planet positions."""

        # alert ephem of starfield properties
        self.ephem = ephem.Observer()
        self.ephem.lon = self.lng
        self.ephem.lat = self.lat

        # ephem uses utctime
        self.ephem.date = datetime.strftime(self.utctime, EPHEM_DTIME_FORMAT)


    def get_timezone(self):
        """return the timezone based on the lat/lng and desired time.

        localtime is a naive (non-timezone-aware) datetime object.

        Use python tzwhere library api to get timezone."""

        # if lat/lng don't have known time zone, return UTC
        # TODO: inform user of this error
        timezone_str = TZW.tzNameAt(self.lat_deg, self.lng_deg) or 'Etc/UTC'

        return pytz.timezone(timezone_str)


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
            local_tz = self.get_timezone()

            # give it a time zone
            local_tz.localize(dtime_local)

            # translate to utc
            self.utctime = to_utc(local_tz, dtime_local)


    def get_display_coords(self, ra, dec):
        """Return alt and az (for this starfield) for a particular ra and dec

        * ra and dec are Decimal objects (in radians)

        return value: dictionary, with these keys / values

            'alt': altitude (in radians)
            'az': azimuth (in radians)
        """

        # assume ra and dec come in as Decimal objects
        coords = RADec(float(ra), float(dec))

        ha = coords.hourAngle(self.utctime, self.lng)
        altaz = coords.altAz(ha, self.lat)

        return {'alt': altaz.alt, 'az': altaz.az}


    def get_stars(self):
        """Return list of star dicts in for the starfield.

        Returns all stars, even if they're not visible, for smooth celestial
        sphere rotation. 

        star dict keys: 
            "alt": altitude for star, in radians
            "az": azimuth for star, in radians
            "magnitude": magnitude of star
            "color": color corresponding to star's spectral class
            "name": star's name

        sample output: 

        [ {"alt": 1.334, "az": 0.1355, "magnitude": 1.7, "color": "#ffffff", "name": "alpha Ori"}
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

            # names based on the constellation aren't interesting (and often 
            # obscure the traditional names); don't include them
            name = star.name
            if star.name and star.const_code and star.name[-3:].lower() == star.const_code.lower():
                name = None

            # convert RA and dec into alt and az
            altaz = self.get_display_coords(star.ra, star.dec)

            # add it to the list in a neat little package
            #
            # cast magnitude to float, as it comes back as a Decimal obj: bad json
            star_field.append({'alt': altaz['alt'], 
                               'az': altaz['az'], 
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
        * list of lists; each sublist contains dicts with 'alt' and 'az' keys, 
        representing an independent line for this constellation. Coordinates are
        in radians format based on the starfield's lat, lng, and the time

        """

        line_groups = []
        for grp in const.line_groups:
            grp_verts = []
            for vert in grp.constline_vertices:
                altaz = self.get_display_coords(vert.star.ra, vert.star.dec)
                grp_verts.append(altaz)

            line_groups.append(grp_verts)

        return line_groups


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
            altaz = self.get_display_coords(vert.ra, vert.dec)
            bound_verts.append(altaz)

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
        line_groups = self.get_const_line_groups(const)

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


    def get_planet_data(self, planet):
        """Return a dict of planet data for the ephem object and planet object.

        Returns None if planet is not visible for this starfield.

        Example planet dict: 
        {'name': 'Jupiter',
         'x': 117.34,
         'y': 489.13,
         'magnitude': -2.21,
         'color': '#ffffc8'
         'size': 3.4 } # size is in arcsec


         Note: Moon also has two more keys: 
            * colong (the angle of the terminus of the lit hemisphere, in degrees)
            * rotation (the angle to rotate the image of the moon, along the
                axis pointing toward earth, in degrees)
        """

        # using the ephemeris way of getting data for a planet for this date
        pla = planet(self.ephem)

        # if it's too dim, don't return it
        if pla.mag > self.max_mag:
            return None

        # otherwise, gather data
        planet_data = {}

        planet_data['alt'] = pla.alt
        planet_data['az'] = pla.az
        planet_data['magnitude'] = pla.mag
        planet_data['name'] = pla.name
        planet_data['color'] = PLANET_COLORS_BY_NAME[pla.name]
        planet_data['size'] = pla.size


        # for the moon, include the angle of the terminus of the lit half, 
        # for phase drawing purposes
        if planet == ephem.Moon:

            # translate colong into degrees
            planet_data['colong'] = rad_to_deg(pla.colong)

            # get the angle rotate the lit moon (in degrees)
            # planet_data['rotation'] = -23.5 * math.cos(pla.hlong)
            planet_data['rotation'] = -23.5 * math.cos(ephem.Ecliptic(pla).lon)

            planet_data['hlong'] = rad_to_deg(pla.hlong)

        return planet_data


    def get_planets(self):
        """Return a list of planet data dicts, transformed for d3.

        see get_planet_data docstring for description of planet data dict
        """

        planets = []

        for planet in NON_STARS:
            pdata = self.get_planet_data(planet)
            if pdata:
                planets.append(pdata)

        return planets


    def get_moon(self):
        """return a dict of moon data, transformed for d3. 

        Since the moon is drawn so differently from the other planets (rendering
        phases), it doesn't make sense to keep it in the same list as the planets

        See get_planet_data docstring for dict details. 
        """

        return self.get_planet_data(ephem.Moon)