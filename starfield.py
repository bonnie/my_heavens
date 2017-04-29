"""Starfield object and methods for calculating stars and constellation display."""

    # Copyright (c) 2017 Bonnie Schulkin

    # This file is part of My Heavens.

    # My Heavens is free software: you can redistribute it and/or modify it under
    # the terms of the GNU Affero General Public License as published by the Free
    # Software Foundation, either version 3 of the License, or (at your option)
    # any later version.

    # My Heavens is distributed in the hope that it will be useful, but WITHOUT
    # ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    # FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
    # for more details.

    # You should have received a copy of the GNU Affero General Public License
    # along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

import os
import math
from math import sin, cos, atan2
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
EPHEM_DTIME_FORMAT = '%Y/%m/%d %H:%M:%S'

# time format to send to front end for display
DISPLAY_TIME_FORMAT = '%-I:%M %p'

# date format to send to front end for display
DISPLAY_DATE_FORMAT = '%B %-d, %Y'

# for getting time zones
GOOGLE_TZ_URL = 'https://maps.googleapis.com/maps/api/timezone/json'

# optional debugging output
DEBUG = False


def deg_to_rad(angle):
    """Return angle (in degrees) translated into radians"""

    return float(angle) / 180 * math.pi


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

        # set the local time zone
        self.set_timezone()

        # set the localtime and utctime
        self.set_time(localtime_string)

        # make an ephemeris for planetary data
        self.make_ephem()

    def __repr__(self):
        """Helpful representation when printed."""

        return '< Starfield lat={}, lng={}, utctime={} >'.format(self.lat,
                                                                 self.lng,
                                                                 self.utctime)

    def get_lat_or_lng_string(self, lat_or_lng):
        """Return a formatted string of the lat or lng for this starfield.

        lat_or_lng is a string: either 'lat' or 'lng' depending on whether you
        want the latitude or longitude.

        Return value looks like this: '122&deg; W'
        """

        if lat_or_lng == 'lat':
            val = abs(self.lat)
            direction = 'N' if self.lat > 0 else 'S'
        else:
            val = abs(self.lng)
            direction = 'E' if self.lng > 0 else 'W'

        return '{:.2f}&deg; {}'.format(val, direction)

    def get_specs(self):
        """Return a dict of specs for this starfield, for front end display."""

        specs = {}
        specs['lat'] = self.get_lat_or_lng_string('lat')
        specs['lng'] = self.get_lat_or_lng_string('lng')
        specs['dateString'] = datetime.strftime(self.localtime, DISPLAY_DATE_FORMAT)
        specs['timeString'] = datetime.strftime(self.localtime, DISPLAY_TIME_FORMAT)

        return specs

    def make_ephem(self):
        """Generate an ephemeris for pyEphem planet positions."""

        # alert ephem of starfield properties
        self.ephem = ephem.Observer()

        # ephem wants lat/lng in radians
        self.ephem.lon = str(self.lng)
        self.ephem.lat = str(self.lat)

        # ephem uses utctime
        self.ephem.date = self.utctime

    def set_timezone(self):
        """return the timezone based on the lat/lng and desired time.

        localtime is a naive (non-timezone-aware) datetime object.

        Use python tzwhere library api to get timezone."""

        # if lat/lng don't have known time zone, return UTC
        # TODO: make guesses based on longitude: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # TODO: inform user if error
        timezone_str = TZW.tzNameAt(self.lat, self.lng) or 'Etc/UTC'

        self.timezone = pytz.timezone(timezone_str)

    def set_time(self, localtime_string):
        """Sets self.utctime based on the local time and the lat/lng.

        * localtime_string is, well, a string
        """

        if not localtime_string:
            # no time like the present!
            naive_utctime = datetime.utcnow()
            self.utctime = pytz.utc.localize(naive_utctime)
            self.localtime = self.utctime.astimezone(self.timezone)

        else:

            # get localtime with no timezone
            dtime_local = datetime.strptime(localtime_string, BOOTSTRAP_DTIME_FORMAT)

            # give it a time zone
            self.timezone.localize(dtime_local)
            self.localtime = dtime_local

            # translate to utc
            self.utctime = to_utc(self.timezone, dtime_local)

    def get_local_from_ephem(self, ephem_date):
        """Return datetime obj for local time zone, corresponding to ephem date.

        ephem_date is in the ephem.Date format, and is in utc.
        """

        dtime = datetime.strptime(str(ephem_date), EPHEM_DTIME_FORMAT)
        dtime_utc = dtime.replace(tzinfo=pytz.UTC)
        dtime_local = dtime_utc.astimezone(self.timezone)

        return dtime_local

    def get_rise_set_times(self, obj):
        """Return tuple of (rise_time, set_time) for the object in question.

        Since this will only show for objects currently visible, the previous
        rise and the next set will be informative.

        Times will be strings in the format DISPLAY_TIME_FORMAT.
        """

        prev_rise = self.ephem.previous_rising(obj)
        prev_rise_local = self.get_local_from_ephem(prev_rise)
        prev_rise_string = prev_rise_local.strftime(DISPLAY_TIME_FORMAT)

        next_set = self.ephem.next_setting(obj)
        next_set_local = self.get_local_from_ephem(next_set)
        next_set_string = next_set_local.strftime(DISPLAY_TIME_FORMAT)

        return (prev_rise_string, next_set_string)

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

        # invert the RA for inside sphere viewing
        planet_data['ra'] = 360 - rad_to_deg(pla.ra)
        planet_data['dec'] = rad_to_deg(pla.dec)

        planet_data['magnitude'] = pla.mag
        planet_data['name'] = pla.name
        planet_data['color'] = PLANET_COLORS_BY_NAME[pla.name]
        planet_data['size'] = pla.size
        planet_data['distance'] = '{:.3f}'.format(pla.earth_distance)
        planet_data['distanceUnits'] = 'AU'
        planet_data['phase'] = '{:.1f}'.format(pla.phase)
        planet_data['celestialType'] = 'planet'

        # ephem.constellation gives a tuple of (abbrev, full name)
        planet_data['constellation'] = ephem.constellation(pla)[1]

        # get rising and setting times
        prev_rise, next_set = self.get_rise_set_times(pla)
        planet_data['prevRise'] = prev_rise
        planet_data['nextSet'] = next_set

        # set attributes for sun and moon for later use
        if pla.name == 'Sun':
            self.sun = pla

        if pla.name == 'Moon':
            self.moon = pla

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

    def get_moon_phase_phrase(self):
        """Get a phrase (e.g. waxing crescent) to describe the moon phase.

        Returns a tuple (waxwan, full_phrase) -- both strings.

        waxwan is simply the first word in the phrase, for use in determing
        rotation.

        This function is more efficient if self.moon has already been set, but
        will set it if not.
        """

        # the tolerance for exact moon phases new, full, quarter
        tolerance = 0.05

        try:
            moon = self.moon
        except AttributeError:
            moon = ephem.Moon(self.ephem)
            self.moon = moon

        # take care of new and full
        if moon.phase < tolerance:
            return '', 'new moon'

        if 100 - moon.phase < tolerance:
            return '', 'full moon'

        # otherwise it's in between
        next_new = ephem.next_new_moon(self.ephem.date)
        next_full = ephem.next_full_moon(self.ephem.date)

        if next_new < next_full:
            growth = 'waning'
        else:
            growth = 'waxing'

        # is it a quarter?
        if abs(moon.phase - 50) < tolerance:
            if growth == 'waxing':
                return growth, 'first quarter'

            # otherwise it's waning: third quarter
            return growth, 'third quarter'

        # most likely: an in between state
        if moon.phase < 50:
            phase = 'crescent'
        else:
            phase = 'gibbous'

        full_phrase = '{} {}: {:.1f}'.format(growth, phase, moon.phase)

        return growth, full_phrase

    def calculate_moon_angle(self, waxwan):
        """Calculate the rotation angle of the phased moon for displaying in d3.

        waxwan will be the first word of the moon phase phrase. It will be on
        of these:
            new (moon)
            full (moon)
            third (quarter)
            first (quarter)
            waxing (crescent / gibbous)
            waning (crescent / gibbous)

        Returns the angle to rotate the moon, in degrees, using a formula from
        http://hrcak.srce.hr/file/197562. This formula gives angle from
        horizontal, not from top of screen, so the azimuth must be added to give
        screen angle.

        """

        # alt/az does not work (MUCH to my consternation) if I try to save the
        # calculated sun and moon as attributes when they're processed in
        # get_planet_data. Why? I'm not sure. For now, just recalculating, as it
        # works. Will possibly try to understand later.

        sun = ephem.Sun(self.ephem)
        moon = ephem.Moon(self.ephem)

        # the position angle of the mid- point of the moon's bright limb,
        #     measured from the horizontal point of the disk (using alt / az)
        # Three cheers for http://hrcak.srce.hr/file/197562 ! 
        #
        # note: switching x and y would give angle to north
        delta_az = sun.az - moon.az
        y = math.sin(delta_az)
        x = math.cos(moon.alt) * math.tan(sun.alt) - math.sin(moon.alt) * math.cos(delta_az)

        # angle to the horizon
        moon_rotation_to_horiz = math.atan2(x, y)

        # so total rotation needs to take into account the horizon angle, aka
        # the azimuth
        moon_rotation = moon_rotation_to_horiz + moon.az

        # adjust depending on phase 
        if waxwan == 'waxing' or waxwan == 'first':
            moon_rotation = moon_rotation + math.pi

        return rad_to_deg(moon_rotation)

    def get_moon(self):
        """Return a dict of moon data, transformed for d3.

        Since the moon is drawn so differently from the other planets (rendering
        phases), it doesn't make sense to keep it in the same list as the planets

        See get_planet_data docstring for dict details.
        """

        moon_data = self.get_planet_data(ephem.Moon)
        moon_data['celestialType'] = 'moon'

        # more digits for the moon, because the number's small
        moon_data['distance'] = '{:.5f}'.format(self.moon.earth_distance)

        # translate colong into degrees
        moon_data['colong'] = rad_to_deg(self.moon.colong)

        # moon gets descriptive phase info
        waxwan, full_phrase = self.get_moon_phase_phrase()
        moon_data['phase'] = full_phrase

        # calculate rotation of the moon disk on d3 dislay
        # waxing / waning (first word in phase phrase) is important to this
        moon_rotation_in_deg = self.calculate_moon_angle(waxwan)
        moon_data['rotation'] = moon_rotation_in_deg

        return moon_data

    def get_sun(self):

        """Return a dict of moon data, transformed for d3.

        Since the sun is important for determining the background, it gets its
        own data dict.

        See get_planet_data docstring for dict details.
        """

        sun_data = self.get_planet_data(ephem.Sun)
        sun_data['celestialType'] = 'star'

        return sun_data

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
