"""--------------------------------------------------------------------------#
# Imports
# --------------------------------------------------------------------------"""

import re
import validate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, SelectMultipleField,
                     DateTimeField, BooleanField, TextAreaField,
                     HiddenField, IntegerField, ValidationError)
from wtforms.validators import (DataRequired, AnyOf, URL, Optional, Length)
from validate import (Phone, ReduiredIfChecked, IsUnique, AnyOfMultiple,
                      RecordExists, DateInRange, ValidDateTime,
                      CompareDate, DateAvailable, timeToString)
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
        validators=[ReduiredIfChecked(check_box='seeking_venue',
                    message=validate.seeking_d_error),
                    Length(max=500, message=validate.text_500_error)]
    )
    available_start = StringField(
        'start_time',
        validators=[ReduiredIfChecked(check_box='seeking_venue',
                                      message=validate.date_error),
                    ValidDateTime(),
                    CompareDate(compare_date_field='available_end',
                                operator='>',
                                message=validate.start_date_error),
                    DateInRange()]
    )
    available_end = StringField(
        'start_time',
        validators=[ReduiredIfChecked(check_box='seeking_venue',
                                      message=validate.date_error),
                    ValidDateTime(),
                    CompareDate(compare_date_field='available_start',
                                operator='<',
                                message=validate.end_date_error),
                    DateInRange()]
    )


#  ----------------------------------------------------------------
#  Show form
#  ----------------------------------------------------------------


class ShowForm(FlaskForm):
    class Meta:
        csrf = False

    artist_id = IntegerField(
        'artist_id',
        validators=[DataRequired(message=validate.integer_error),
                    RecordExists(table=Artist, check_field='id',
                                 message=validate.artist_id_error)]
    )
    venue_id = IntegerField(
        'venue_id',
        validators=[DataRequired(message=validate.integer_error),
                    RecordExists(table=Venue, check_field='id',
                                 message=validate.venue_id_error)]

    )
    start_time = StringField(
        'start_time',
        validators=[DataRequired(),
                    ValidDateTime(),
                    DateInRange(),
                    DateAvailable()],
        default=timeToString(datetime.today())
    )
