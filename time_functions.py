"""functions for manipulating datetimes and time zones"""

from datetime import datetime
import pytz


def to_utc(tz, dtime):
    """takes a timezone-aware datetime object, and returns a utc datetime object

    from http://stackoverflow.com/questions/1357711/pytz-utc-conversion
    This is more complete than dtime.astimezone(pytz.utc), since it deals with
    daylight savings, etc.
    """

    return tz.normalize(tz.localize(dtime)).astimezone(pytz.utc)

