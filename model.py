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


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Constellation code=%s name=%s>" % (self.const_code, self.name)


class Star(db.Model):
    """Star in the universe."""

    __tablename__ = "stars"

    star_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    const_code = db.Column(db.String(3), db.ForeignKey("constellations.const_code"))
    name = db.Column(db.String(128), nullable=True)
    ra = db.Column(db.Numeric(6, 3), nullable=False)  # in degrees
    dec = db.Column(db.Numeric(6, 3), nullable=False)  # in degrees
    distance = db.Column(db.Numeric(12, 2), nullable=True)  # in parsecs
    magnitude = db.Column(db.Numeric(4, 2), nullable=False)
    absolute_magnitude = db.Column(db.Numeric(5, 3), nullable=True)
    spectrum = db.Column(db.String(16), nullable=False)
    color_index = db.Column(db.Numeric(4, 3), nullable=True)
    color = db.Column(db.String(7), nullable=False)

    constellation = db.relationship("Constellation")

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
    ra = db.Column(db.Numeric(6, 3), nullable=False) # in degrees
    dec = db.Column(db.Numeric(6, 3), nullable=False) # in degrees

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

def connect_to_db(app, db_uri='postgresql:///star_chart'):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
