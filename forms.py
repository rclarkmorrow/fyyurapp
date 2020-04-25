import re
from datetime import datetime
from flask_wtf import Form
from wtforms import (StringField, SelectField, SelectMultipleField,
                     DateTimeField, BooleanField, TextAreaField,
                     ValidationError)
from wtforms.validators import DataRequired, AnyOf, URL, Optional, Length

# Forms


class VenueForm(Form):
    class Meta:
        csrf = False

    def validate_phone(form, field):
        if (not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data)
                and not re.search(r"^[0-9]{10}$", field.data)):
            raise ValidationError('Please enter a valid US phone number' +
                                  '<br />("123-456-7890" or "1234567890")')

    def validate_seeking_description(form, field):
        if form.seeking_talent.data is True and field.data == '':
            raise ValidationError('Please enter details below.')

    name = StringField(
        'name', validators=[DataRequired(),
                            Length(max=120,
                                   message='Can\'t be more than 120 ' +
                                   'characters')]
    )
    city = StringField(
        'city', validators=[DataRequired(),
                            Length(max=120,
                                   message='Can\'t be more than 120 ' +
                                   'characters')]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired(),
                               Length(max=120,
                                      message='Can\'t be more than 120 ' +
                                      'characters.')]
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(),
                                  URL(message='Please enter a valid URL.' +
                                      '<br />("http://" or "https://" is ' +
                                      'required)'),
                                  Length(max=500,
                                         message='<br />Can\'t be more than ' +
                                         '500 characters.')]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
    )
    website = StringField(
        'website', validators=[Optional(),
                               URL(message='Please enter a valid URL' +
                                   '<br />("http://" or "https://" ' +
                                   'is required)'),
                               Length(max=120,
                                      message='<br />Can\'t be more than ' +
                                      '120 characters.')]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(),
                                     URL(message='Please enter a' +
                                         ' valid facebook link.' +
                                         '<br />("http://" or "https://" ' +
                                         'is required)'),
                                     Length(max=120,
                                            message='<br />Can\'t be more ' +
                                            'than 120 characters.')]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[Length(max=500,
                                                  message='Can\'t be more ' +
                                                  'than 500 characters.')]
    )


class ArtistForm(Form):
    class Meta:
        csrf = False

    def validate_phone(form, field):
        if (not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data)
                and not re.search(r"^[0-9]{10}$", field.data)):
            raise ValidationError('Please enter a valid US phone number' +
                                  '<br />("123-456-7890" or "1234567890")')

    def validate_seeking_description(form, field):
        if form.seeking_talent.data is True and field.data == '':
            raise ValidationError('Please enter details below.')

    name = StringField(
        'name', validators=[DataRequired(),
                            Length(max=120,
                                   message='Can\'t be more than 120 ' +
                                   'characters')]
    )
    city = StringField(
        'city', validators=[DataRequired(),
                            Length(max=120,
                                   message='Can\'t be more than 120 ' +
                                   'characters')]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(),
                                  URL(message='Please enter a valid URL.' +
                                      '<br />("http://" or "https://" is ' +
                                      'required)'),
                                  Length(max=500,
                                         message='<br />Can\'t be more than ' +
                                         '500 characters.')]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
    )
    website = StringField(
        'website', validators=[Optional(),
                               URL(message='Please enter a valid URL' +
                                   '<br />("http://" or "https://" ' +
                                   'is required)'),
                               Length(max=120,
                                      message='<br />Can\'t be more than ' +
                                      '120 characters.')]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(),
                                     URL(message='Please enter a' +
                                         ' valid facebook link.' +
                                         '<br />("http://" or "https://" ' +
                                         'is required)'),
                                     Length(max=120,
                                            message='<br />Can\'t be more ' +
                                            'than 120 characters.')]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[Length(max=500,
                                                  message='Can\'t be more ' +
                                                  'than 500 characters.')]
    )


class ShowForm(Form):
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
