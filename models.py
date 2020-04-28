"""--------------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------------"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


"""--------------------------------------------------------------------------#
# Models
#--------------------------------------------------------------------------"""


#  ----------------------------------------------------------------
#  Venue model
#  ----------------------------------------------------------------


class Venue(db.Model):
    __tablename__ = 'Venue'

    defaultImg = "https://placebear.com/400/400"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(db.String)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, server_default='f')
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=False, default=defaultImg)


#  ----------------------------------------------------------------
#  Artist model
#  ----------------------------------------------------------------


class Artist(db.Model):
    __tablename__ = 'Artist'

    defaultImg = "https://placekitten.com/2000/2000"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, server_default='f')
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=False, default=defaultImg)


#  ----------------------------------------------------------------
#  Show model
#  ----------------------------------------------------------------


# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.
