"""add star and constellation data to the stars db. """

import csv
import math
import re
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from model import db, connect_to_db, Star, Constellation, ConstLineVertex, \
                  ConstLineGroup, BoundVertex, ConstBoundVertex

from colors import COLOR_BY_SPECTRAL_CLASS

STARDATA_FILE = 'seed_data/hygfull.csv'
CONST_FILE = 'seed_data/const_abbrevs.csv'
CONSTBOUNDS_FILE = 'seed_data/constellation_boundaries.txt'
CONSTLINES_FILE = 'seed_data/constellation_lines.csv'

SC_RE = re.compile(r'([OBAFGKM]\d) ?\(?([VI]*)\)?')

# for cleaning up BayerFlamsteed names
BF_RE = re.compile(r'^\d+\s*')

# for stars with unrecognizable spectral classes
DEFAULT_COLOR = "#ffffff"

def announce(action):
    """Give feedback on where in the script we are."""

    print
    print '*'*20
    print action
    print '*'*20


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
        return DEFAULT_COLOR

def get_name_and_constellation(star_info):
    """get the name and constellation from a line in the STARDATA file"""

    # get the name
    name = star_info['ProperName'].strip()

    # strip unnecessary BayerFlamsteed cruft
    bf = BF_RE.sub('', star_info['BayerFlamsteed'].strip())

    if not name and len(bf) > 3: 
        # if bf is just 3 characters long, it's only the constellation
        name = bf

    # now for the constellation -- it's the last 3 characters of BayerFlamsteed
    if bf:
        constellation = bf[-3:].upper()
    else:
        constellation = None

    return name, constellation


def load_constellations():
    """Load constellation names and abbreviations from csv into db."""

    announce('loading constellations')

    # read in all the constellations and make objects for them
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

    announce('loading constellation boundaries')

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

    announce('loading stars')

    line_num = 0

    with open(STARDATA_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for starline in reader:
            
            # display progress
            line_num += 1
            if line_num % 5000 == 0:
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

            # get name from the best available column
            name, const = get_name_and_constellation(starline)

            star = Star(
                name=name,
                const_code=const,
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


def load_constellation_lines():
    """Add the constellation lines into the db.

    * Each continuous line gets its own line group. 
    * Match stars to existing stars in the db using ra, dec, and magnitude
    """

    announce('loading constellation lines')

    # to track whether it's time for a new group
    group_break = True

    with open(CONSTLINES_FILE) as csvfile:
        reader = csv.DictReader(csvfile)

        for constpoint in reader: 

            # time to make a new group? 
            if not constpoint['RA']:
                group_break = True
                continue

            # get data into proper format
            ra_in_rad, dec_in_rad = get_radian_coords(constpoint['RA'], constpoint['DEC'])
            mag = float(constpoint['MAG'])

            # find the star matching this constellation line point
            query = Star.query.filter(db.func.abs(Star.ra - ra_in_rad) < 0.005, 
                                 db.func.abs(Star.dec - dec_in_rad) < 0.005)

            query_with_magnitude = query.filter(db.func.abs(db.func.abs(Star.magnitude) - db.func.abs(mag)) < 0.5)
                                 
            try: 
                try:
                    star = query_with_magnitude.one()

                except NoResultFound:

                    # some of the magnitudes are way off. Try without the magnitude
                    try:
                        star = query.one()
                        print "matched {} {} without magnitude".format(constpoint['CON'], constpoint['NAME'])

                    except NoResultFound:

                        error = "couldn't find a star match for {} {} ra {} dec {} mag {}"
                        print error.format(constpoint['CON'], constpoint['NAME'], ra_in_rad, dec_in_rad, mag)
                        print "exiting..."
                        exit()

            except MultipleResultsFound:

                # just go with the brightest star that matches the coordinates
                star = query.order_by(Star.magnitude).first()
                print "matched {} {} with brightest star in region".format(constpoint['CON'], constpoint['NAME'])

            # make a new group if necessary
            if group_break: 
                group = ConstLineGroup(const_code = constpoint['CON'])
                db.session.add(group)
                db.session.flush()

                # reset running vars
                index = 0
                group_break = False

            # add this vertex to the db and the group
            vert = ConstLineVertex(const_line_group_id=group.const_line_group_id,
                                star_id=star.star_id,
                                index=index)
            db.session.add(vert)

        db.session.commit()


if __name__ == '__main__':

    from server import app
    connect_to_db(app)


    db.drop_all()
    db.create_all()
    load_constellations()
    load_const_boundaries()
    load_stars()
    load_constellation_lines()