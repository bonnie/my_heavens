"""add data to the stars db. 

csv data downloaded from http://astronexus.com/files/downloads/hygfull.csv.gz"""

import csv
from model import db, Star, connect_to_db
import math

DATA_FILE = 'seed_data/hygfull.csv'

def load_stars():
    """load star data from csv into the database"""

    line_num = 0

    with open(DATA_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for starline in reader:
            
            # display progress
            line_num += 1
            if line_num % 500 == 0:
                print line_num

            # skip really dim stars
            magnitude = float(starline['Mag'].strip())
            if magnitude > 7:
                continue

            # translate ra and dec into radians, for easier sidereal module use
            ra_in_rad = float(starline['RA']) * math.pi / 12
            dec_in_rad = float(starline['Dec']) * math.pi / 180

            star = Star(
                name=starline['ProperName'],
                ra=ra_in_rad,
                dec=dec_in_rad,
                distance=starline['Distance'],
                magnitude=magnitude,
                absolute_magnitude=starline['AbsMag'],
                spectrum=starline['Spectrum'].strip(),
                color_index=starline['ColorIndex'])

            db.session.add(star)

    db.session.commit()


#     name = db.Column(db.String(128), nullable=True)
#     right_ascension = db.Column(db.Integer, nullable=False)
#     declination = db.Column(db.Integer, nullable=False)
#     distance = db.Column(db.Numeric(8, 3), nullable=True)
#     magnitude = db.Column(db.Numeric(3, 2), nullable=False)
#     absolute_magnitude = db.Column(db.Numeric(5, 4), nullable=True)
#     spectrum = db.Column(db.String(8), nullable=False)
#     color_index = db.column(db.Numeric(4, 3))


# StarID,Hip,HD,HR,Gliese,BayerFlamsteed,ProperName,RA,Dec,Distance,Mag,AbsMag,Spectrum,ColorIndex

if __name__ == '__main__':

    from server import app
    connect_to_db(app)


    db.drop_all()
    db.create_all()
    load_stars()