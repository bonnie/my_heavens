"""Flask web server for star charts app"""

import os
from flask import Flask, render_template, jsonify
from datetime import datetime

from model import connect_to_db, Constellation
from starfield import StarField

# display radius
STARFIELD_RADIUS = 400
GOOGLE_KEY = os.environ.get('GOOGLE_KEY')

app = Flask(__name__)


@app.route('/')
def display_chart():
    """display the basic html for the star field. 

    Stars will be filled in with js"""

    return render_template("stars.html", google_key=GOOGLE_KEY)


@app.route('/stars.json')
def return_stars():
    """return a json of star info, along with the radius for the star field 

    stars is a list of dictionaries with these keys: 

    x
    y
    magnitude
    color
    """

    # lat = '51.5074dN' # london
    # lng = '0.1278dE'    # london

    # TODO: get this from user via form inputs
    lat = 37.7749  # san francisco
    lng = -122.4194 # san francisco
    max_magnitude = 5 # dimmest stars to show

    stf = StarField(lat=lat,
                    lng=lng,
                    max_mag=max_magnitude,
                    display_radius=STARFIELD_RADIUS)

    stars = stf.get_stars()
    consts = stf.get_consts()

    return jsonify({'constellations': consts, 
                    'radius': stf.display_radius, 
                    'stars': stars})


if __name__ == '__main__':

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5005)