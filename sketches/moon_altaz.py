from datetime import datetime
# be able to import from parent dir
import sys
sys.path.append('..')

from starfield import StarField, BOOTSTRAP_DTIME_FORMAT

DISPLAY_DATE_FORMAT = '%B %d, %Y'
DISPLAY_TIME_FORMAT = '%I:%M %p'


berk_latlng = ('Berkeley', 37.87, -122.27)
cc_latlng = ('Christchurch', -43.53, 172.64)

dates = [
    'March 28, 2017 at 2:49 PM',
    'March 7, 2017 at 6:00 PM',
    'March 27, 2017 at 9:00 AM',
    'March 22, 2017 at 12:00 PM',
    'March 15, 2017 at 4:00 AM',
    'January 1, 2017 at 12:00 PM',
    'March 1, 2017 at 6:00 PM'
]

# header
print ','.join(['city', 'date', 'lambda', 'phi', 'phase', 'ephAlt', 'ephAz', 'sidAlt', 'sidAz'])

for loc in [berk_latlng, cc_latlng]:
    for date in dates:

        dt = datetime.strptime(date, 
            '{} at {}'.format(DISPLAY_DATE_FORMAT, DISPLAY_TIME_FORMAT))

        datestring = datetime.strftime(dt, BOOTSTRAP_DTIME_FORMAT)
        stf = StarField(loc[1], loc[2], datestring)

        mdata = stf.get_moon()
        rot = stf.get_sky_rotation()

        print ','.join([loc[0], date, str(rot['lambda']), str(rot['phi']), mdata['phase'], 
                        str(mdata['ephAlt']), str(mdata['ephAz']),
                        str(mdata['sidAlt']), str(mdata['sidAz'])])