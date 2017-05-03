"""Flask web server for my heavens app."""

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
from flask import Flask, request, render_template, jsonify

from model import connect_to_db, Constellation
from starfield import StarField
from stars import get_stars, get_constellations
from definitions import DEFINITIONS

# display radius
STARFIELD_RADIUS = 400

app = Flask(__name__)


@app.route('/')
def display_chart():
    """display the basic html for the star field. 

    Stars will be filled in with js"""

    return render_template("main.html", 
                                sorted_terms=sorted(DEFINITIONS.keys()),
                                terms=DEFINITIONS)

@app.route('/terms.json')
def return_terms():
    """Return json of terms, definitions, and wikipedia links."""

    return jsonify(DEFINITIONS)

@app.route('/stars.json')
def return_stars():
    """return a json of star and constellation info
    """

    max_magnitude = 4.5  # dimmest stars to show

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
    max_magnitude = 5  # dimmest planets to show

    stf = StarField(lat=float(lat),
                    lng=float(lng),
                    max_mag=max_magnitude,
                    localtime_string=localtime_string)

    return jsonify({'dateloc': stf.get_specs(),
                    'rotation': stf.get_sky_rotation(),
                    'planets': stf.get_planets(),
                    'sundata': stf.get_sun(), # sun is a reserved word in js!
                    'moon': stf.get_moon()})


if __name__ == '__main__':

    # app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5005)