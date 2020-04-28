"""--------------------------------------------------------------------------#
# Imports
# --------------------------------------------------------------------------"""

import re
from wtforms import ValidationError
from models import db

"""--------------------------------------------------------------------------#
# Validators, error messages and enum choice restrictions
# --------------------------------------------------------------------------"""

#  ----------------------------------------------------------------
#  Custom Validators
#  ----------------------------------------------------------------


class Phone(object):
    def __init__(self, message=None):
        if not message:
            message = ('Please enter a valid US phone number' +
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
            print(selection)
            print(self.choices)
            if selection not in self.choices:
                raise ValidationError(self.message)


class ReduiredIfChecked(object):
    def __init__(self, check_box=None, message=None):
        self.check_box = check_box
        if not message:
            message = ('Please enter details below.')
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
            message = (f'This field must be unique.')
        self.message = message

    def __call__(self, form, field):
        # Conditional validates required inputs, returns exception if not met
        if self.table is None or self.key is None or self.check_field is None:
            raise Exception('Required paramaters not provided to verify ' +
                            'field is unique.')
        else:
            # Queries database for matching record with the table and column
            # provided as parameters.
            # NOTE: this is intentionally case-insensitive
            check_field_value = form._fields.get(self.check_field).data.strip()
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


#  ----------------------------------------------------------------
#  Error messages
#  ----------------------------------------------------------------


text_120_error = 'Can\'t be more than 120 characters'
text_500_error = 'Can\'t be more than 500 characters'
url_error = ('Please enter a valid URL.<br />("http://" or' +
             ' "https://" is required)')
fb_error = ('Please enter a valid facebook link.' +
            '<br />("http://" or "https://" is required)')
state_error = ('Please select a valid state.')
genres_error = ('Please select valid genres.')
venue_name_error = ('This venue name is already listed.')
artist_name_error = ('This artist name is already listed.')


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
