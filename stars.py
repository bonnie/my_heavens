"""Functions for retrieving stars from db and putting them into d3 friendly format."""

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


from model import db, Star, Constellation


def get_stars(max_mag):
    """Return list of star dicts for the given maximum magnitude.

    Returns all stars to populate entire celestial sphere

    star dict keys:
        "ra": right ascension for star, in degrees
        "dec": declination for star, in degrees
        "magnitude": magnitude of star
        "color": color corresponding to star's spectral class
        "name": star's name

    sample output:

    [ {"ra": 88.793, "dec": 7.407, "magnitude": 0.45, "color": "#ffc168", "name": "Betelgeuse"}
        ...
    ]
    """

    # get list of stars with specified max magnitude
    db_stars = Star.query.filter(Star.magnitude <= max_mag).all()
    star_field = []

    for star in db_stars:

        # names based on the constellation aren't interesting (and often
        # obscure the traditional names); don't include them
        name = star.name
        if star.name and star.const_code and star.name[-3:].lower() == star.const_code.lower():
            name = None

        # add it to the list in a neat little package
        #
        # cast numbers to float, as it comes back as a Decimal obj: bad json

        star_field.append({'ra': float(star.ra),
                           'dec': float(star.dec),
                           'magnitude': float(star.magnitude),
                           'absMagnitude': '{:.2f}'.format(float(star.absolute_magnitude)),
                           'specClass': star.spectrum,
                           'constellation': star.constellation.name if star.constellation else None,
                           'color': star.color,
                           'name': name,
                           'distance': float(star.distance),
                           'distanceUnits': 'parsecs',
                           'celestialType': 'star'
                           })

    return star_field


def get_const_line_groups(const):
    """Return a list of constellation line group data for input constellation

    * const is a Constellation instance

    Returns a list of lists: 
    each sublist contains dicts with 'ra' and 'dec' keys, 
    representing an independent line for this constellation. Coordinates are
    in radians format based on the starfield's lat, lng, and the time

    """

    line_groups = []
    for grp in const.line_groups:
        grp_verts = []
        for vert in grp.constline_vertices:
            grp_verts.append([float(vert.star.ra), float(vert.star.dec)])

        line_groups.append(grp_verts)

    return line_groups


def get_const_bound_verts(primary_const, secondary_const=None):
    """Return a dictionary of boundary vertex data, formatted for d3 geoPath LineString

    * const is a Constellation instance

    * secondary_const is also a Constellation instance -- only used in the 
      case of serpens, which has two distinct areas in the sky

    returns a list of lists of coordinates in the form of [ra, dec]

    * for all constellations except serpens, the returned list will have only 
      one list item (but d3 requires this listified list). For serpens, the 
      list will have two items, one for each of its polygons.

    """

    # for d3 (and serpens), there needs to be an outer list
    bounds_list = []

    # go through two consts for serpens; one const otherwise
    consts = [primary_const, secondary_const] if secondary_const else [primary_const]

    for const in consts:

        # collect the boundaries
        coord_list = []

        for vert in const.bound_vertices:
            coord_list.append([float(vert.ra), float(vert.dec)])

        # add the final boundary point to close the boundary loop
        if coord_list:
            coord_list.append(coord_list[0])
            bounds_list.append(coord_list)

    return bounds_list


def get_const_data(const, const_data_1=None, const_data_2=None):
    """Return a dictionary of constellation data, transformed for d3

    * const is a Constellation instance
    
    * const_data_1 and const_data_2 also a Constellation instance -- only used 
      in the case of serpens, which has two distinct areas in the sky. In that 
      case, const is SER, const_data_1 is SER1 (which has the line groups and
      one set of bound verts) and const_data_2 is SER2 (which has the other set
      of bound verts)

    Coordinates for boundary vertices and constellation lines are in 
    ra and dec format

    returned dict has this format: 

    'code': <string>
    'name': <string>
    'bound_verts': <list of lists of lists of coordinates> # d3 required format
    'line_groups': <list of lists of lists of coordinates>

    for the line_groups list, each sub-list represents an independent line
    for this constellation (see get_const_line_groups).
    """

    # temporary dict to store data for this constellation
    c = {}

    c['code'] = const.const_code
    c['name'] = const.name

    # get the constellation lines and boundaries

    if const_data_1:
        # oh, serpens
        c['line_groups'] = get_const_line_groups(const_data_1)
        c['bound_verts'] = get_const_bound_verts(const_data_1, const_data_2)    

    else: 
        c['line_groups'] = get_const_line_groups(const)
        c['bound_verts'] = get_const_bound_verts(const)

    return c    


def get_constellations():
    """Return a list of constellation data dicts, transformed for d3.

    Returns a list of dicts of constellation data.
    See docstring for get_const_data for details on constellation dicts.
    """

    consts = []

    # do joinedloads to make the data collection faster
    query = db.session.query(Constellation)
    const_joins = query.options(
                        db.joinedload("bound_vertices"),
                        db.joinedload("line_groups"))

    consts_raw = const_joins.all()

    for const_raw in consts_raw:
    
        # oh, serpens
        # Serpens has two distinct constellation boundaries, but one set of 
        # constellation lines. Sigh. 
        if const_raw.name.startswith('Serpens'):

            # just skip SE1 and SE2 -- they are only there to hold info for 
            # the unified constellation
            if const_raw.const_code in ['SE1', 'SE2']:
                continue

            # otherwise, we've got the main constellation
            se1_raw = Constellation.query.get('SE1')
            se2_raw = Constellation.query.get('SE2')
            const_data = get_const_data(const_raw, se1_raw, se2_raw)

        else:
            # for those well-behaved non-serpens constellations
            const_data = get_const_data(const_raw)

        consts.append(const_data)

    return consts
