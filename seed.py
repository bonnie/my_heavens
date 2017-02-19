"""add data to the stars db. 

csv data downloaded from http://astronexus.com/files/downloads/hygfull.csv.gz"""

import csv
import math
import re
from sqlalchemy.orm.exc import NoResultFound

from model import db, connect_to_db, Star, Constellation, ConstLineVertex, \
                  ConstLineGroup, BoundVertex, ConstBoundVertex

from colors import COLOR_BY_SPECTRAL_CLASS

STARDATA_FILE = 'seed_data/hygfull.csv'
CONST_FILE = 'seed_data/const_abbrevs.csv'
CONSTBOUNDS_FILE = 'seed_data/constellation_boundaries.txt'
CONSTLINES_FILE = 'seed_data/constellation_lines.txt'

SC_RE = re.compile(r'([OBAFGKM]\d) ?\(?([VI]*)\)?')

# for stars with unrecognizable spectral classes
DEFAULT_COLOR = "#ffffff"


def get_radian_coords(ra_in_hrs, dec_in_degs):
    """return a tuple of radian equivalents of input (input in string format) 

    right ascension input in hours, declination input in degrees"""

    ra_in_rad = float(ra_in_hrs) * math.pi / 12
    dec_in_rad = float(dec_in_degs) * math.pi / 180

    return ra_in_rad, dec_in_rad


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


def load_constellations():
    """Load constellation names and abbreviations from csv into db."""

    print
    print '*'*20, 'loading constellations'


    # a dict to store constellations and their associated data
    constellations = {}

    # first read in all the constellations and make objects for them
    with open(CONST_FILE) as csvfile:
        reader = csv.DictReader(csvfile)

        # make a new const obj for each line and add to db
        for constline in reader: 
            newconst = Constellation(const_code=constline['Abbrev'],
                                     name=constline['Name'])
            db.session.add(newconst)

    db.session.commit()

def load_const_boundaries():
    """Add the boundary vertices for each constellation into the db"""

    print
    print '*'*20, 'loading constellation boundaries'

    boundfile = open(CONSTBOUNDS_FILE)
    
    # keep track of what constellation we're on, in order to reset indexes when
    # we switch constellations
    last_const = None

    for boundline in boundfile:
        try: 
            ra, dec, const = boundline.strip().split()
        except: 
            print "bad line in boundfile: [{}]".format(boundline) 
            continue

        # translate ra and dec into radians
        ra_in_rad, dec_in_rad = get_radian_coords(ra, dec)

        # reset the index if necessary
        if const != last_const:
            index = 0
            last_const = const

        # account for the fact that the input file has greater precision than
        # what's stored in the db
        rounded_ra = int(ra_in_rad * 1000) / 1000.0
        rounded_dec = int(dec_in_rad * 1000) / 1000.0

        # create the vertex, if it doesn't already exist
        try:
            vertex = BoundVertex.query.filter_by(ra=rounded_ra, dec=rounded_dec).one()

        except NoResultFound:
            vertex = BoundVertex(ra=ra_in_rad, dec=dec_in_rad)
            db.session.add(vertex)

            # to get an id, and make available for future iterations
            db.session.flush()

        # add the vertex to the constellation boundary
        const_bound_vertex = ConstBoundVertex(const_code=const,
                                              vertex_id=vertex.vertex_id,
                                              index=index)
        db.session.add(const_bound_vertex)


        # increment the index
        index += 1

    db.session.commit()

def load_stars():
    """Load star data from csv into the database."""

    print
    print '*'*20, 'loading stars'

    line_num = 0

    with open(STARDATA_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for starline in reader:
            
            # display progress
            line_num += 1
            if line_num % 500 == 0:
                print line_num, 'stars'

            # skip really dim stars
            magnitude = float(starline['Mag'].strip())
            if magnitude > 7:
                continue

            # translate ra and dec into radians, for easier sidereal module use
            ra_in_rad, dec_in_rad = get_radian_coords(starline['RA'], starline['Dec'])

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


if __name__ == '__main__':

    from server import app
    connect_to_db(app)


    db.drop_all()
    db.create_all()
    # load_stars()
    load_constellations()
    load_const_boundaries()
