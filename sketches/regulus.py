# RA 10h 8m 22s | Dec -11° 58′ 2″

from sidereal.sidereal import parseLon, parseLat, parseAngle, RADec, hoursToRadians
from datetime import datetime, timedelta


# sidereal module needs "d" for degrees and then the direction(NSEW)
sf_lat_in_degrees = '37.7749dN'
sf_lon_in_degrees = '122.4194dW'

sf_lat_in_rad = parseLat(sf_lat_in_degrees)
sf_lon_in_rad = parseLon(sf_lon_in_degrees)

ra_in_hours = 10 + 8.0/60 + 22.0/3600
dec_in_degrees = '11d58m60s'

ra_in_rad = hoursToRadians(ra_in_hours)
dec_in_rad = parseAngle(dec_in_degrees)

coords = RADec(ra_in_rad, dec_in_rad)

thiseve = datetime.utcnow() + timedelta(hours=10)

ha = coords.hourAngle(thiseve, sf_lon_in_rad)
altaz = coords.altAz(ha, sf_lat_in_rad)

