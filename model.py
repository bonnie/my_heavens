"""database model and functions for star_charts project"""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class Star(db.Model):
    """Star in the universe."""

    __tablename__ = "stars"

    star_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    ra = db.Column(db.Numeric(5, 3), nullable=False) # in radians
    dec = db.Column(db.Numeric(5, 3), nullable=False) # in radians
    distance = db.Column(db.Numeric(12, 2), nullable=True)
    magnitude = db.Column(db.Numeric(4, 2), nullable=False)
    absolute_magnitude = db.Column(db.Numeric(5, 3), nullable=True)
    spectrum = db.Column(db.String(16), nullable=False)
    color_index = db.Column(db.Numeric(4, 3), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Star star_id=%s name=%s ra=%s dec=%s>" % (self.star_id, 
                                                           self.name,
                                                           self.ra,
                                                           self.dec)

    
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
