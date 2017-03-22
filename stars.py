"""functions for retrieving stars from db and putting them into d3 friendly format"""

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
                           'color': star.color,
                           'name': name,
                           'distance': float(star.distance),
                           'distanceUnits': 'parsecs',
                           'type': 'star'
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


def get_const_bound_verts(const):
    """Return a dictionary of boundary vertex data, formatted for d3 geoPath LineString

    * const is a Constellation instance

    returns a list of coordinates in the form of [ra, dec])
    """

    # collect the boundaries
    coord_list = []

    for vert in const.bound_vertices:
        coord_list.append([float(vert.ra), float(vert.dec)])

    # add the final boundary point to close the boundary loop
    if coord_list:
        coord_list.append(coord_list[0])

    return coord_list


def get_const_data(const):
    """Return a dictionary of constellation data, transformed for d3

    * const is a Constellation instance

    Coordinates for boundary vertices and constellation lines are in 
    ra and dec format

    returned dict has this format: 

    'code': <string>
    'name': <string>
    'bound_verts': <list of dicts with 'ra' and 'dec' keys>
    'line_groups': <list of lists of dicts with 'ra' and 'dec' keys>

    for the line_groups list, each sub-list represents an independent line
    for this constellation (see get_const_line_groups).
    """

    # temporary dict to store data for this constellation
    c = {}

    c['code'] = const.const_code
    c['name'] = const.name

    # get the constellation lines and boundaries
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
     
        const_data = get_const_data(const_raw)
        consts.append(const_data)

    return consts
