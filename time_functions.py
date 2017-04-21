"""Functions for manipulating datetimes and time zones."""

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

from datetime import datetime
import pytz

def to_utc(tz, dtime):
    """takes a timezone-aware datetime object, and returns a utc datetime object

    from http://stackoverflow.com/questions/1357711/pytz-utc-conversion
    This is more complete than dtime.astimezone(pytz.utc), since it deals with
    daylight savings, etc.
    """

    return tz.normalize(tz.localize(dtime)).astimezone(pytz.utc)


