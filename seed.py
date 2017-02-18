"""add data to the stars db. 

csv data downloaded from http://astronexus.com/files/downloads/hygfull.csv.gz"""

import csv
import math
import re

from model import db, Star, connect_to_db
from colors import COLOR_BY_SPECTRAL_CLASS

DATA_FILE = 'seed_data/hygfull.csv'
SC_RE = re.compile(r'([OBAFGKM]\d) ?\(?([VI]*)\)?')

# for stars with unrecognizable spectral classes
DEFAULT_COLOR = "#ffffff"

def get_color(spectral_class):
    """get hex color from spectral class"""

    match = SC_RE.search(spectral_class)
    if match:
        sc_a = match.group(1)
        sc_b = match.group(2)

        # unrecognized base spectrum
        if sc_a not in COLOR_BY_SPECTRAL_CLASS:
            print "spectrum not in color dict: {} {}".format(sc_a, sc_b)
            return DEFAULT_COLOR

        # missing secondary spectrum
        if not sc_b or sc_b not in COLOR_BY_SPECTRAL_CLASS[sc_a]:
            # just pick a random color from this spectral class
            spectral_colors = COLOR_BY_SPECTRAL_CLASS[sc_a]
            return spectral_colors[spectral_colors.keys()[0]]

        # if we got to here, all's well
        return COLOR_BY_SPECTRAL_CLASS.get(sc_a).get(sc_b)

    else:
        # we've got ourselves a white star!
        print "unclassifiable spectrum: {}".format(spectral_class)
        return DEFAULT_COLOR

def load_stars():
    """load star data from csv into the database"""

    line_num = 0

    with open(DATA_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for starline in reader:
            
            # display progress
            line_num += 1
            if line_num % 500 == 0:
                print line_num

            # skip really dim stars
            magnitude = float(starline['Mag'].strip())
            if magnitude > 7:
                continue

            # translate ra and dec into radians, for easier sidereal module use
            ra_in_rad = float(starline['RA']) * math.pi / 12
            dec_in_rad = float(starline['Dec']) * math.pi / 180

            # sometimes color_index is a bunch of space characters
            if re.match(r"\S", starline['ColorIndex']):
                color_index = starline['ColorIndex']
            else:
                color_index = None

            # get color from spectral class
            spectrum = starline['Spectrum'].strip()
            color = get_color(spectrum)

            star = Star(
                name=starline['ProperName'],
                ra=ra_in_rad,
                dec=dec_in_rad,
                distance=starline['Distance'],
                magnitude=magnitude,
                absolute_magnitude=starline['AbsMag'],
                spectrum=spectrum,
                color_index=color_index,
                color=color)

            db.session.add(star)

    db.session.commit()


#     name = db.Column(db.String(128), nullable=True)
#     right_ascension = db.Column(db.Integer, nullable=False)
#     declination = db.Column(db.Integer, nullable=False)
#     distance = db.Column(db.Numeric(8, 3), nullable=True)
#     magnitude = db.Column(db.Numeric(3, 2), nullable=False)
#     absolute_magnitude = db.Column(db.Numeric(5, 4), nullable=True)
#     spectrum = db.Column(db.String(8), nullable=False)
#     color_index = db.column(db.Numeric(4, 3))


# StarID,Hip,HD,HR,Gliese,BayerFlamsteed,ProperName,RA,Dec,Distance,Mag,AbsMag,Spectrum,ColorIndex

if __name__ == '__main__':

    from server import app
    connect_to_db(app)


    db.drop_all()
    db.create_all()
    load_stars()