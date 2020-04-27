import re
import validate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, SelectMultipleField,
                     DateTimeField, BooleanField, TextAreaField,
                     HiddenField, ValidationError)
from wtforms.validators import (DataRequired, AnyOf, URL, Optional, Length)
from validate import Phone, ReduiredIfChecked, IsUnique
from models import Venue, Artist

# Forms


class VenueForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField()

    name = StringField(
        'name', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error),
                            IsUnique(table=Venue, key='id',
                                     check_field='name',)]
    )
    city = StringField(
        'city', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error)]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
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
        'genres', validators=[DataRequired()],
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
        'seeking_talent'
    )
    seeking_description = TextAreaField(
        'seeking_description',
        validators=[ReduiredIfChecked(check_box='seeking_talent'),
                    Length(max=500, message=validate.text_500_error)]
    )
    print(seeking_talent)


class ArtistForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField()

    name = StringField(
        'name', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error),
                            IsUnique(table=Artist, key='id',
                                     check_field='name')]
    )
    city = StringField(
        'city', validators=[DataRequired(),
                            Length(max=120,
                                   message=validate.text_120_error)]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
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
        'genres', validators=[DataRequired()],
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
        'seeking_venue'
    )
    seeking_description = TextAreaField(
        'seeking_description',
        validators=[ReduiredIfChecked(check_box='seeking_venue'),
                    Length(max=500, message=validate.text_500_error)]
    )


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )
