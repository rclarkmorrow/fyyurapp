"""--------------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------------"""


import datetime
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
    # Main Model
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
    # Relationships
    shows = db.relationship('Show', back_populates='venue', lazy=True)


#  ----------------------------------------------------------------
#  Artist model
#  ----------------------------------------------------------------


class Artist(db.Model):
    __tablename__ = 'Artist'

    defaultImg = "https://placekitten.com/2000/2000"
    # Main model
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
    available_start = db.Column(db.DateTime)
    available_end = db.Column(db.DateTime)
    # Relationships
    shows = db.relationship('Show', back_populates='artist', lazy=True)

#  ----------------------------------------------------------------
#  Show model
#  ----------------------------------------------------------------


class Show(db.Model):
    __tablename__ = 'Show'
    # Main model
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id',
                          ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id',
                         ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    # Relationships
    venue = db.relationship('Venue', back_populates='shows', lazy=True)
    artist = db.relationship('Artist', back_populates='shows', lazy=True)
