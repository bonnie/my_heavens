"""add star and constellation data to the stars db. """

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
import sys
import csv
import re
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from model import db, connect_to_db, Star, Constellation, ConstLineVertex, \
                  ConstLineGroup, BoundVertex, ConstBoundVertex

from colors import COLOR_BY_SPECTRAL_CLASS

# for debugging output. False by default unless running the script directly.
DEBUG = False

# to be able to distinguish between data dir for testing
DATADIR = 'seed_data'

# for spectral classes
SC_RE = re.compile(r'([OBAFGKM]\d) ?\(?([VI]*)\)?')

# for cleaning up BayerFlamsteed names
BF_RE = re.compile(r'^\d+\s*')

# for stars with unrecognizable spectral classes
DEFAULT_COLOR = "#ffffff"


def open_datafile(datadir, file_type):
    """Return path to the data file type using the datadir as the location.

    Handy for testing when using a different datadir"""

    if file_type == 'stars':
        filename = 'hygfull.csv'

    elif file_type == 'consts':
        filename = 'const_abbrevs.csv'

    elif file_type == 'bounds':
        filename = 'constellation_boundaries.txt'

    elif file_type == 'lines':
        filename = 'constellation_lines.csv'

    else:
        return None

    return open(os.path.join(datadir, filename))


def announce(action):
    """Give feedback on where in the script we are."""

    if DEBUG:
        print
        print '*' * 20
        print action
        print '*' * 20


def get_degrees_from_hours_and_invert(ra_in_hrs):
    """Return a degree equivalent of input RA in hours and invert.

    Inversion (subtraction from 360) is necessary to simulate looking at the
    *inside* of the celestial sphere in d3, instead of the outside

    (input in string or Decimal format)"""

    return 360 - float(ra_in_hrs) * 360 / 24


def get_color(spectral_class):
    """get hex color from spectral class"""

    match = SC_RE.search(spectral_class)
    if match:
        sc_a = match.group(1)
        sc_b = match.group(2)

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
    name = star_info['ProperName'].strip() or None

    # strip unnecessary BayerFlamsteed cruft
    bf = star_info['BayerFlamsteed'].strip()
    bf = re.sub(r' +', ' ', bf)
    bf = re.sub(r'^[\d ]+', '', bf)

    if not name and len(bf) > 3:
        # if bf is just 3 characters long, it's only the constellation
        name = bf

    # now for the constellation -- it's the last 3 characters of BayerFlamsteed
    if bf:
        constellation = bf[-3:].upper()
    else:
        constellation = None

    return name, constellation


def load_constellations(datadir):
    """Load constellation names and abbreviations from csv into db."""

    announce('loading constellations')

    # read in all the constellations and make objects for them
    with open_datafile(datadir, 'consts') as csvfile:
        reader = csv.DictReader(csvfile)

        # make a new const obj for each line and add to db
        for constline in reader:
            newconst = Constellation(const_code=constline['Abbrev'],
                                     name=constline['Name'])
            db.session.add(newconst)

    db.session.commit()


def get_bounds_vertex(ra_in_deg, dec_in_deg):
    """Search for the bounds vertex matching the input. Create a new one if needed.

    ra_in_deg and dec_in_deg are floats.

    returns BoundsVertex object.

    """

    # account for the fact that the input file has greater precision than
    # what's stored in the db
    rounded_ra = int(ra_in_deg * 1000) / 1000.0
    rounded_dec = int(dec_in_deg * 1000) / 1000.0

    # create the vertex, if it doesn't already exist
    try:
        vertex = BoundVertex.query.filter_by(ra=rounded_ra, dec=rounded_dec).one()

    except NoResultFound:
        vertex = BoundVertex(ra=ra_in_deg, dec=dec_in_deg)
        db.session.add(vertex)

        # to get an id, and make available for future iterations
        db.session.flush()

    return vertex


def load_const_boundaries(datadir):
    """Add the boundary vertices for each constellation into the db"""

    announce('loading constellation boundaries')

    boundfile = open_datafile(datadir, 'bounds')

    # keep track of what constellation we're on, in order to reset indexes when
    # we switch constellations
    last_const = None

    for boundline in boundfile:
        ra_in_hrs, dec, const = boundline.strip().split()

        # translate ra into degrees and invert for d3
        ra_in_deg = get_degrees_from_hours_and_invert(ra_in_hrs)
        dec_in_deg = float(dec)

        # reset the index if necessary
        if const != last_const:
            index = 0
            last_const = const

        vertex = get_bounds_vertex(ra_in_deg, dec_in_deg)

        # add the vertex to the constellation boundary
        const_bound_vertex = ConstBoundVertex(const_code=const,
                                              vertex_id=vertex.vertex_id,
                                              index=index)
        db.session.add(const_bound_vertex)


        # increment the index
        index += 1

    db.session.commit()


def load_stars(datadir):
    """Load star data from csv into the database."""

    announce('loading stars')

    line_num = 0

    with open_datafile(datadir, 'stars') as csvfile:
        reader = csv.DictReader(csvfile)
        for starline in reader:

            # display progress
            line_num += 1
            if DEBUG and line_num % 5000 == 0:
                print '{} stars'.format(line_num)

            # skip really dim stars
            magnitude = float(starline['Mag'].strip())
            if magnitude > 7:
                continue

            # translate ra into degrees and invert for d3
            ra_in_deg = get_degrees_from_hours_and_invert(starline['RA'])
            dec_in_deg = float(starline['Dec'])

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
                ra=ra_in_deg,
                dec=dec_in_deg,
                distance=starline['Distance'],
                magnitude=magnitude,
                absolute_magnitude=starline['AbsMag'],
                spectrum=spectrum,
                color_index=color_index,
                color=color)

            db.session.add(star)

    db.session.commit()


def get_matching_star(ra_in_deg, dec_in_deg, mag, const=None, name=None):
    """Get the closest star matching the input values.

    const and name are strings used only for debugging.

    Returns a Star object"""

   # find the star matching this constellation line point
    query = Star.query.filter(db.func.abs(Star.ra - ra_in_deg) < 0.02,
                         db.func.abs(Star.dec - dec_in_deg) < 0.02)

    query_with_magnitude = query.filter(db.func.abs(db.func.abs(Star.magnitude) - db.func.abs(mag)) < 0.5)

    try:
        try:
            star = query_with_magnitude.one()

        except NoResultFound:

            # some of the magnitudes are way off (variable stars?). Try without the magnitude
            try:
                star = query.one()
                if DEBUG:
                    print "matched {} {} without magnitude".format(const, name)

            except NoResultFound:

                if DEBUG:
                    error = "couldn't find a star match for {} {} ra {} dec {} mag {}"
                    print error.format(const, name, ra_in_deg, dec_in_deg, mag)
                    print "exiting..."
                exit()

    except MultipleResultsFound:

        # just go with the brightest star that matches the coordinates
        star = query.order_by(Star.magnitude).first()
        if DEBUG:
            print "matched {} {} with brightest star in region".format(const, name)

    return star


def load_constellation_lines(datadir):
    """Add the constellation lines into the db.

    * Each continuous line gets its own line group.
    * Match stars to existing stars in the db using ra, dec, and magnitude
    """

    announce('loading constellation lines')

    # to track whether it's time for a new group
    group_break = True

    with open_datafile(datadir, 'lines') as csvfile:
        reader = csv.DictReader(csvfile)

        for constpoint in reader:

            # time to make a new group?
            if not constpoint['RA']:
                group_break = True
                continue

            # translate degrees to hours and invert
            ra_in_deg = get_degrees_from_hours_and_invert(constpoint['RA'])

            # get data into proper format
            dec_in_deg = float(constpoint['DEC'])
            mag = float(constpoint['MAG'])

            # find the matching star in the db
            star = get_matching_star(ra_in_deg, dec_in_deg, mag, constpoint['CON'], constpoint['NAME'])

            # make a new group if necessary
            if group_break:
                group = ConstLineGroup(const_code=constpoint['CON'])
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


def load_seed_data(ddir):
    """Run all the functions to load the seed data.

    For ease in seeding test database with one line of code."""

    load_constellations(ddir)
    load_const_boundaries(ddir)
    load_stars(ddir)
    load_constellation_lines(ddir)


if __name__ == '__main__':

    # don't import app from server; we don't want to have to wait for the
    # the tzwhere instance
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)

    # if we're running it directly, we probably want to see debug
    DEBUG = True

    print 'dropping tables...'
    db.drop_all()

    print 'creating tables...'
    db.create_all()

    load_seed_data(DATADIR)
