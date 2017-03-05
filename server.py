"""Flask web server for star charts app"""

import os
from flask import Flask, request, render_template, jsonify

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


@app.route('/stars.json', methods=['POST'])
def return_stars():
    """return a json of star and constellation info, plus star field radius
    """

    lat = request.form.get('lat')
    lng = request.form.get('lng')
    localtime_string = request.form.get('datetime')
    max_magnitude = 5 # dimmest stars to show

    stf = StarField(lat=lat,
                    lng=lng,
                    max_mag=max_magnitude,
                    localtime_string=localtime_string,
                    display_radius=STARFIELD_RADIUS)

    stars = stf.get_stars()
    consts = stf.get_consts()
    planets = stf.get_planets()

    return jsonify({'constellations': consts, 
                    'radius': stf.display_radius, 
                    'stars': stars,
                    'planets': planets})


if __name__ == '__main__':

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5005)