"""--------------------------------------------------------------------------#
# Imports
# --------------------------------------------------------------------------"""

import re
import datetime
from wtforms import ValidationError, DateTimeField
from models import db, Artist, Venue, Show

"""--------------------------------------------------------------------------#
# Validators, error messages and enum choice restrictions
# --------------------------------------------------------------------------"""

#  ----------------------------------------------------------------
#  Custom Validators
#  ----------------------------------------------------------------


class Phone(object):
    def __init__(self, message=None):
        if not message:
            message = ('Please enter a valid US phone number'
                       '<br />("123-456-7890 or "1234567890")')
        self.message = message

    def __call__(self, form, field):
        # Regex validates whether inputed phone number meets requirements
        if (not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data)
                and not re.search(r"^[0-9]{10}$", field.data)):
            raise ValidationError(self.message)


class AnyOfMultiple(object):
    def __init__(self, choices=None, message=None):
        self.choices = choices
        if not message:
            message = ('Please select valid choices.')
        self.message = message

    def __call__(self, form, field):

        # Checks each selection in a MultipleSelectField against
        # against values in passed choices list.
        for selection in field.data:
            if selection not in self.choices:
                raise ValidationError(self.message)


class ReduiredIfChecked(object):
    def __init__(self, check_box=None, message=None):
        self.check_box = check_box
        if not message:
            message = (f'This field is required if the box '
                       f'{check_box} is selected')
        self.message = message

    def __call__(self, form, field):
        # Requires base field to have data if specified check box is
        # true.
        check_box_value = form._fields.get(self.check_box)

        if check_box_value.data is True and field.data.strip() == '':
            raise ValidationError(self.message)


class IsUnique(object):
    def __init__(self, table=None, key=None,
                 check_field=None, message=None):
        self.table = table
        self.key = key
        self.check_field = check_field

        if not message:
            message = 'This field must be unique.'
        self.message = message

    def __call__(self, form, field):
        # Conditional validates required inputs, returns exception if not met
        if self.table is None or self.key is None or self.check_field is None:
            raise Exception('Required paramaters not provided to verify '
                            'field is unique.')

        # Queries database for matching record with the table and column
        # provided as parameters.
        # NOTE: this is intentionally case-insensitive to allow for whacky
        # capitalization schemes some bands are known for.
        check_field_value = field.data.strip()
        key_value = int((form._fields.get(self.key).data) or -1)
        record_query = (
            self.table.query
            .filter(getattr(self.table, self.check_field)
                    == check_field_value).first()
        )
        # If a record is returned checks for field value match and record
        # id mismatch. Raises validation error if both conditions are met.
        if record_query is not None:
            if (getattr(record_query, self.check_field).strip()
                    == check_field_value and (key_value) !=
                    ((getattr(record_query, self.key)))):
                raise ValidationError(self.message)


class RecordExists(object):
    def __init__(self, table=None, check_field=None, message=None):
        self.table = table
        self.check_field = check_field

        if not message:
            message = 'The record does not exist'
        self.message = message

    def __call__(self, form, field):
        if self.table is None or self.check_field is None:
            raise Exception('The required parameters not provided '
                            'to verify record exists')

        # Checks that the record with the ID entered in the field exists
        # in the specified table.
        check_field_value = field.data
        record_query = (
            self.table.query
            .filter(getattr(self.table, self.check_field)
                    == check_field_value).first()
        )

        if record_query is None:
            raise ValidationError(self.message)


class CompareDate(object):
    def __init__(self, compare_date_field=None, operator=None, message=None):
        if not message:
            if operator == '=':
                message = ('The compared date fields are not equivalent.')
            elif operator == '<':
                message = ('The current date field is not before the '
                           'compared date field.')
            elif operator == '>':
                message = ('The current date field is not after the '
                           'compared date field.')
            else:
                raise Exception('Valid comparison operator not provided.')

        self.message = message
        self.compare_date_field = compare_date_field
        self.operator = operator

    def __call__(self, form, field):
        try:
            compare_date = stringToDateTime(form._fields.get(
                self.compare_date_field).data.strip())
            self_date = stringToDateTime(field.data.strip())
        except ValueError:
            raise ValueError('')

        if (self.compare_date_field is not None and self.operator is not None
                and compare_date is not None and self_date is not None):

            # Compares date entered in date field to a date in specified
            # date field with the specified operator.
            if self.operator == '=':
                if self_date != compare_date:
                    raise ValidationError(self.message)

            if self.operator == '<':
                if self_date < compare_date:
                    raise ValidationError(self.message)

            if self.operator == '>':
                if self_date > compare_date:
                    raise ValidationError(self.message)


class DateInRange(object):
    def __init__(self, start_time='2010-01-01 00:00',
                 end_time='2031-01-01 00:00', message=None):
        try:
            self.start_time = stringToDateTime(start_time)
            self.end_time = stringToDateTime(end_time)
        except ValueError:
            raise Exception('Invalid start and end time parameters')

        if not message:
            message = ('Please enter a date between '
                       f'{timeToString(self.start_time)} and '
                       f'{timeToString(self.end_time)}.')
        self.message = message

    def __call__(self, form, field):
        # Verifies that date entered in field falls between the default or
        # specified time range.
        if field.data.strip() != '':
            try:
                this_time = stringToDateTime(field.data.strip())
            except ValueError:
                raise ValueError('')
            if this_time <= self.start_time or this_time >= self.end_time:
                raise ValidationError(self.message)


class DateAvailable(object):
    def __init__(self, show_time_delta=2):
        self.show_time_delta = show_time_delta

    def __call__(self, form, field):
        artist_id = int((form._fields.get('artist_id').data) or -1)

        if artist_id > -1:
            artist_query = Artist.query.get(artist_id)
            artist_start = artist_query.available_start
            artist_end = artist_query.available_end
        else:
            raise Exception('')

        artist_shows = Show.query.filter(Show.artist_id == artist_id).all()
        this_date = stringToDateTime(field.data.strip())

        # Verifies that the entered time is within artist's availability.
        if (this_date != '' and artist_start is not None and
                artist_end is not None):
            if this_date <= artist_start or this_date >= artist_end:
                raise ValidationError(
                    f'{artist_query.name} is available between '
                    f'{timeToString(artist_start)} and '
                    f'{timeToString(artist_end)}.'
                )
        # Verifies that the time is not too close to another booking.
        # The default is two hours but can be set with the show_time_delta
        # parameter.
        for show in artist_shows:
            show_delta = datetime.timedelta(hours=self.show_time_delta)
            start_time = show.start_time - show_delta
            end_time = show.start_time + show_delta
            if this_date >= start_time and this_date <= end_time:
                raise ValidationError(
                    f'{artist_query.name} is already booked on '
                    f'{show.venue.name} at {show.start_time} '
                    f'please pick a time {self.show_delta} hours '
                    'before or after that time.'
                )


class ValidDateTime(object):
    def __init__(self, message=None):
        if not message:
            message = 'Please enter a time in YYYY-MM-DD HH:MM format'
        self.message = message

    def __call__(self, form, field):
        # If date field is not an empty string or white space, checks that
        # date entered in the field is formatted correctly (note uses the
        # format specified in the stringToDateTime function).
        if field.data.strip() != '':
            try:
                stringToDateTime(field.data.strip())
            except ValueError:
                raise ValidationError(self.message)


#  ----------------------------------------------------------------
#  Functions
#  ----------------------------------------------------------------


# Function converts input datetime string into datetime object.
def stringToDateTime(date_string):
    if date_string == '':
        return None
    return datetime.datetime.strptime(date_string.strip(), '%Y-%m-%d %H:%M')


# Function converts datetime object to string.
def timeToString(timestamp):
    return datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M')


#  ----------------------------------------------------------------
#  Error messages
#  ----------------------------------------------------------------


text_120_error = 'Can\'t be more than 120 characters'
text_500_error = 'Can\'t be more than 500 characters'
url_error = ('Please enter a valid URL.<br />("http://" or'
             ' "https://" is required)')
fb_error = ('Please enter a valid facebook link.'
            '<br />("http://" or "https://" is required)')
state_error = 'Please select a valid state.'
genres_error = 'Please select valid genres.'
venue_name_error = 'This venue name is already listed.'
artist_name_error = 'This artist name is already listed.'
artist_id_error = 'This artist ID is not listed.'
venue_id_error = 'This venue ID is not listed.'
date_error = 'Please enter a show time in YYYY-MM-DD HH:MM format.'
seeking_d_error = 'Please enter details below.'
integer_error = 'Please enter a valid number.'
end_date_error = 'End time must be after start time.'
start_date_error = 'Start time must be before end time.'

#  ----------------------------------------------------------------
#  Enum data for restricted choices
#  ----------------------------------------------------------------


state_choices = [
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
state_list = [choice[1] for choice in state_choices]

genre_choices = [
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
genre_list = [choice[1] for choice in genre_choices]
