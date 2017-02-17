"""Flask web server for star charts app"""

from flask import Flask, render_template, jsonify
from model import connect_to_db
from calculations import get_user_star_coords


app = Flask(__name__)


@app.route('/')
def display_chart():

    return render_template("stars.html")

@app.route('/stars.json')
def return_stars():

    # TODO: get this from user via form inputs
    lat = '37.7749dN'  # san francisco
    lng = '122.4194dW' # san francisco
    utc_now = datetime.utcnow()  # current time

    stars = get_user_star_coords(lat, lng, utc_now)

    return jsonify({'stars': stars})


if __name__ == '__main__':

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5005)