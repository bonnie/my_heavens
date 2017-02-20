"""database model and functions for star_charts project"""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class Constellation(db.Model):
    """Constellation names and codes."""

    __tablename__ = "constellations"

    ##### columns #####
    const_code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(64), nullable=False)


    ##### relationships #####
    bound_vertices = db.relationship("BoundVertex",
                             secondary="const_bound_vertices",
                             order_by="ConstBoundVertex.index")

    stars = db.relationship("Star")

    line_groups = db.relationship("ConstLineGroup")


    ##### methods #####
    @classmethod
    def get_constellation_data(cls):
        """Return a list of constellation data dicts.

        each dict has this format: 

        'code': <string>
        'name': <string>
        'bound_verts': <list of dicts with 'ra' and 'dec' keys>
        'line_groups': <list of lists of dicts with 'ra' and 'dec' keys>

        for the line_groups list, each sub-list represents an independent line
        for this constellation.
        """

        constellation_data = []

        # do joinedloads to make the data collection faster
        query = cls.query
        const_joins = query.options(
                            db.joinedload("bound_vertices"),
                            db.joinedload("line_groups"))

        consts = const_joins.all()

        # consts = cls.query.all()

        for const in consts:

            # temporary dict to store data for this constellation
            c = {}

            c['code'] = const.const_code
            c['name'] = const.name

            # collect the boundaries
            c['bound_verts'] = [
                                 {'ra': float(vert.ra), 'dec':float(vert.dec)} 
                                 for vert in const.bound_vertices
                               ]

            # get the constellation lines
            c['line_groups'] = [ 
                                 [
                                   {'ra': float(vert.star.ra), 'dec': float(vert.star.dec)} 
                                   for vert in grp.constline_vertices
                                 ] 
                                 for grp in const.line_groups
                               ]

            constellation_data.append(c)


        return constellation_data

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Constellation code=%s name=%s>" % (self.const_code, self.name)


class Star(db.Model):
    """Star in the universe."""

    __tablename__ = "stars"

    star_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    const_code = db.Column(db.String(3), db.ForeignKey("constellations.const_code"))
    name = db.Column(db.String(128), nullable=True)
    ra = db.Column(db.Numeric(5, 3), nullable=False) # in radians
    dec = db.Column(db.Numeric(5, 3), nullable=False) # in radians
    distance = db.Column(db.Numeric(12, 2), nullable=True)
    magnitude = db.Column(db.Numeric(4, 2), nullable=False)
    absolute_magnitude = db.Column(db.Numeric(5, 3), nullable=True)
    spectrum = db.Column(db.String(16), nullable=False)
    color_index = db.Column(db.Numeric(4, 3), nullable=True)
    color = db.Column(db.String(7), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Star star_id=%s name=%s ra=%s dec=%s>" % (self.star_id, 
                                                           self.name,
                                                           self.ra,
                                                           self.dec)

class ConstLineVertex(db.Model):
    """a vertex that forms one endpoint of a constellation line. 

    this corresponds to a star"""

    __tablename__ = "const_line_vertices"

    const_line_vertex_id = db.Column(db.Integer, 
                            autoincrement=True, 
                            primary_key=True)

    const_line_group_id = db.Column(db.Integer, 
                            db.ForeignKey("const_line_group.const_line_group_id"), 
                            nullable=False)

    star_id = db.Column(db.Integer, 
                            db.ForeignKey("stars.star_id"), 
                            nullable=False)

    # where in the constellation line sequence is this? 
    index = db.Column(db.Integer, nullable=False)

    ##### relationships #####
    star = db.relationship("Star")


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<ConstLineVertex id=%s const_code=%s star_id>" % (
                                            self.const_line_vertex_id,
                                            self.const_code, 
                                            self.star_id)


class ConstLineGroup(db.Model):
    """a group of vertices that make up a continuous constellation line"""

    __tablename__ = "const_line_group"

    const_line_group_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    const_code = db.Column(db.String(3), db.ForeignKey("constellations.const_code"), nullable=False)

    # be able to get a list of stars in this group easily
    constline_vertices = db.relationship("ConstLineVertex",
                                         order_by="ConstLineVertex.index")


class BoundVertex(db.Model):
    """Vertices of constellation boundaries, not attached to constellations.

    Each vertex can be a part of multiple constellation boundaries, and 
    each constellation boundary is made up of multiple vertices."""

    __tablename__ = "bound_vertices"

    vertex_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ra = db.Column(db.Numeric(5, 3), nullable=False) # in radians
    dec = db.Column(db.Numeric(5, 3), nullable=False) # in radians

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<BoundVertex id=%s ra=%s dec=%s>" % (self.vertex_id, 
                                                      self.ra,
                                                      self.dec)

class ConstBoundVertex(db.Model):
    """Constellation boundary vertices.

    Association table between Constellation and BoundVertex"""

    __tablename__ = "const_bound_vertices"

    const_bound_vertex_id = db.Column(db.Integer, 
                                autoincrement=True, 
                                primary_key=True)

    const_code = db.Column(db.String(3), 
                            db.ForeignKey('constellations.const_code'), 
                            nullable=False)

    vertex_id = db.Column(db.Integer, 
                            db.ForeignKey('bound_vertices.vertex_id'), 
                            nullable=False)

    # the order in the vertex list for this constellation vertex
    index = db.Column(db.Integer, nullable=False) 


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<ConstBoundVertex id=%s const_code=%s vertex_id=%s>" % (
                                                          self.const_bound_vertex_id, 
                                                          self.const_code,
                                                          self.vertex_id)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///star_chart'
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
