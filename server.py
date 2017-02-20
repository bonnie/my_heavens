"""Flask web server for star charts app"""

from flask import Flask, render_template, jsonify
from datetime import datetime

from model import connect_to_db, Constellation
from calculations import get_user_star_coords
from display_constants import STARFIELD_RADIUS


app = Flask(__name__)


@app.route('/')
def display_chart():
    """display the basic html for the star field. 

    Stars will be filled in with js"""

    return render_template("stars.html")

@app.route('/stars.json')
def return_stars():
    """return a json of star info, along with the radius for the star field 

    stars is a list of dictionaries with these keys: 

    x
    y
    magnitude
    color
    """

    # TODO: get this from user via form inputs
    lat = '37.7749dN'  # san francisco
    lng = '122.4194dW' # san francisco
    utc_now = datetime.utcnow()  # current time
    max_magnitude = 5 # dimmest stars to show

    stars = get_user_star_coords(lat, lng, utc_now, max_magnitude)
    constellations = Constellation.get_constellation_data()

    return jsonify({'constellations': constellations, 
                    'radius': STARFIELD_RADIUS, 
                    'stars': stars})


if __name__ == '__main__':

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5005)