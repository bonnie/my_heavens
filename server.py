"""Flask web server for star charts app"""

import os
from flask import Flask, request, render_template, jsonify

from model import connect_to_db, Constellation
from starfield import StarField
from stars import get_stars, get_constellations

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
    """return a json of star and constellation info
    """

    max_magnitude = 5  # dimmest stars to show

    return jsonify({'constellations': get_constellations(),
                    'stars': get_stars(max_magnitude)})


@app.route('/place-time-data.json', methods=['POST'])
def return_place_time_data():
    """Return json of sky rotation, planet, sun and moon info.

    Returned data is based on location and time from POST data.
    """

    lat = request.form.get('lat')
    lng = request.form.get('lng')
    localtime_string = request.form.get('datetime')
    max_magnitude = 5  # dimmest stars to show

    stf = StarField(lat=float(lat),
                    lng=float(lng),
                    max_mag=max_magnitude,
                    localtime_string=localtime_string)

    return jsonify({'rotation': stf.get_sky_rotation(),
                    'planets': stf.get_planets(),
                    'moon': stf.get_moon(),
                    'sun': stf.get_sun()})


if __name__ == '__main__':

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5005)