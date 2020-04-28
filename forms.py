"""--------------------------------------------------------------------------#
# Imports
# --------------------------------------------------------------------------"""

import re
import validate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, SelectMultipleField,
                     DateTimeField, BooleanField, TextAreaField,
                     HiddenField, ValidationError)
from wtforms.validators import (DataRequired, AnyOf, URL, Optional, Length)
from validate import Phone, ReduiredIfChecked, IsUnique, AnyOfMultiple
from models import Venue, Artist, Show


"""--------------------------------------------------------------------------#
# Forms
# --------------------------------------------------------------------------"""


#  ----------------------------------------------------------------
#  Venue form
#  ----------------------------------------------------------------


class VenueForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField()

    name = StringField(
        'name', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error),
                            IsUnique(table=Venue, key='id',
                                     check_field='name',
                                     message=validate.venue_name_error)]
    )
    city = StringField(
        'city', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error)]
    )
    state = SelectField(
        'state', validators=[DataRequired(),
                             AnyOf(validate.state_list,
                                   message=validate.state_error)],
        choices=validate.state_choices
    )
    address = StringField(
        'address', validators=[DataRequired(),
                               Length(max=120,
                                      message=validate.text_120_error)]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Phone()]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(),
                                  URL(message=validate.url_error),
                                  Length(max=500,
                                         message=validate.text_500_error)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(),
                              AnyOfMultiple(choices=validate.genre_list,
                                            message=validate.genres_error)],
        choices=validate.genre_choices
    )
    website = StringField(
        'website', validators=[Optional(),
                               URL(message=validate.url_error),
                               Length(max=120,
                                      message=validate.text_120_error)]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(),
                                     URL(message=validate.fb_error),
                                     Length(max=120,
                                            message=validate.text_120_error)]
    )
    seeking_talent = BooleanField(
        'seeking_talent', validators=[AnyOf([True, False])]
    )
    seeking_description = TextAreaField(
        'seeking_description',
        validators=[ReduiredIfChecked(check_box='seeking_talent'),
                    Length(max=500, message=validate.text_500_error)]
    )


#  ----------------------------------------------------------------
#  Artist form
#  ----------------------------------------------------------------


class ArtistForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField()

    name = StringField(
        'name', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error),
                            IsUnique(table=Artist, key='id',
                                     check_field='name',
                                     message=validate.artist_name_error)]
    )
    city = StringField(
        'city', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error)]
    )
    state = SelectField(
        'state', validators=[DataRequired(),
                             AnyOf(validate.state_list,
                                   message=validate.state_error)],
        choices=validate.state_choices
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Phone()]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(),
                                  URL(message=validate.url_error),
                                  Length(max=500,
                                         message=validate.text_500_error)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(),
                              AnyOfMultiple(choices=validate.genre_list,
                              message=validate.genres_error)],
        choices=validate.genre_choices
    )
    website = StringField(
        'website', validators=[Optional(),
                               URL(message=validate.url_error),
                               Length(max=120,
                                      message=validate.text_120_error)]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(),
                                     URL(message=validate.fb_error),
                                     Length(max=120,
                                            message=validate.text_120_error)]
    )
    seeking_venue = BooleanField(
        'seeking_venue', validators=[AnyOf([True, False])]
    )
    seeking_description = TextAreaField(
        'seeking_description',
        validators=[ReduiredIfChecked(check_box='seeking_venue'),
                    Length(max=500, message=validate.text_500_error)]
    )


#  ----------------------------------------------------------------
#  Show form
#  ----------------------------------------------------------------


class ShowForm(FlaskForm):
    class Meta:
        csrf = False

    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(message='The artist ID has a problem')] 
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(message='The venue ID has a problem.')]

    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired(message='The time has a problem.')],
        default=datetime.today()
    )
