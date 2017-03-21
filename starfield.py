"""Starfield object and methods for calculating stars and constellation display"""

import math
from datetime import datetime
from sidereal import sidereal
import pytz
from tzwhere import tzwhere
import ephem

from time_functions import to_utc
from colors import PLANET_COLORS_BY_NAME

# it takes some time to initialize this, so do it once when the file loads
TZW = tzwhere.tzwhere()

# to determine which non-star objects to find
PLANETS = [ephem.Mercury, ephem.Venus, ephem.Mars,
           ephem.Jupiter, ephem.Saturn, ephem.Neptune, ephem.Uranus]

# how datetime comes in from bootstrap. For example "2017-01-01T01:00"
BOOTSTRAP_DTIME_FORMAT = '%Y-%m-%dT%H:%M'

# how ephem expects / gives dates
EPHEM_DTIME_FORMAT = '%Y/%-m/%-d %H:%M:%S'

# for getting time zones
GOOGLE_TZ_URL = 'https://maps.googleapis.com/maps/api/timezone/json'

# optional debugging output
DEBUG = False


def deg_to_rad(angle):
    """Return angle (in degrees) translated into radians"""

    return angle / 180 * math.pi


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
        self.lat = lat
        self.lng = lng

        # translate local time to utc if necessary
        if localtime_string is None:
            self.utctime = datetime.utcnow()
        else:
            self.set_utc_time(localtime_string)

        # make an ephemeris for planetary data
        self.make_ephem()

    def __repr__(self):
        """Helpful representation when printed."""

        return '< Starfield lat={}, lng={}, utctime={} >'.format(self.lat,
                                                                 self.lng,
                                                                 self.utctime)

    def make_ephem(self):
        """Generate an ephemeris for pyEphem planet positions."""

        # alert ephem of starfield properties
        self.ephem = ephem.Observer()

        # ephem wants lat/lng in radians
        self.ephem.lon = deg_to_rad(self.lng)
        self.ephem.lat = deg_to_rad(self.lat)

        # ephem uses utctime
        self.ephem.date = datetime.strftime(self.utctime, EPHEM_DTIME_FORMAT)

    def get_timezone(self):
        """return the timezone based on the lat/lng and desired time.

        localtime is a naive (non-timezone-aware) datetime object.

        Use python tzwhere library api to get timezone."""

        # if lat/lng don't have known time zone, return UTC
        # TODO: make guesses based on longitude: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # TODO: inform user if error
        timezone_str = TZW.tzNameAt(self.lat, self.lng) or 'Etc/UTC'

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

    def get_planet_data(self, planet):
        """Return a dict of planet data for the ephem object and planet object.

        Returns None if planet is not visible for this starfield.

        Example planet dict:
        {'name': 'Jupiter',
         'ra': 117.34,
         'dec': 489.13,
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

        # invert the RA for better inside sphere viewing
        planet_data['ra'] = 360 - rad_to_deg(pla.ra)
        planet_data['dec'] = rad_to_deg(pla.dec)

        planet_data['magnitude'] = pla.mag
        planet_data['name'] = pla.name
        planet_data['color'] = PLANET_COLORS_BY_NAME[pla.name]
        planet_data['size'] = pla.size

        # for the moon, include the longitude of the terminus of the lit half,
        # for phase drawing purposes, plus calculate the rotation
        if planet == ephem.Moon:

            # translate colong into degrees
            planet_data['colong'] = rad_to_deg(pla.colong)

            # get the angle rotate the lit moon (in degrees)
            # planet_data['rotation'] = -23.5 * math.cos(pla.hlong)
            # planet_data['rotation'] = -23.5 * math.cos(ephem.Ecliptic(pla).lon)

            planet_data['hlong'] = rad_to_deg(pla.hlong)

        return planet_data

    def get_planets(self):
        """Return a list of planet data dicts, transformed for d3.

        see get_planet_data docstring for description of planet data dict
        """

        planets = []

        for planet in PLANETS:
            pdata = self.get_planet_data(planet)
            if pdata:
                planets.append(pdata)

        return planets

    def get_moon(self):
        """Return a dict of moon data, transformed for d3.

        Since the moon is drawn so differently from the other planets (rendering
        phases), it doesn't make sense to keep it in the same list as the planets

        See get_planet_data docstring for dict details.
        """

        return self.get_planet_data(ephem.Moon)

    def get_sun(self):

        """Return a dict of moon data, transformed for d3.

        Since the sun is important for determining the background, it gets its
        own data dict.

        See get_planet_data docstring for dict details.
        """

        return self.get_planet_data(ephem.Sun)

    def get_sky_rotation(self):
        """Return d3 sky rotation for this starfield.

        Return value is a dict in the format:

        { 'lambda': lambda (in degrees),
          'phi': phi (in degrees) }
        """

        # the lambda rotation depends on the right ascension that's transiting
        # at the given latitude and time. The sidereal module's hourAngleToRa
        # calculates this nicely. The hour angle is 0 for the meridian.
        ha_in_rad = sidereal.hourAngleToRA(0, self.utctime, deg_to_rad(self.lng))
        lda = rad_to_deg(ha_in_rad)

        # the phi rotation is dependent solely on the latitude
        phi = -1 * self.lat

        return {'lambda': lda, 'phi': phi}
