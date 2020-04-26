"""--------------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------------"""
import sys
import json
import dateutil.parser
import babel
from flask import (Flask, render_template, request, Response, flash,
                   redirect, url_for, jsonify)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

"""--------------------------------------------------------------------------#
# App Config.
#--------------------------------------------------------------------------"""

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


"""--------------------------------------------------------------------------#
# Models.
#--------------------------------------------------------------------------"""


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


# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.


"""--------------------------------------------------------------------------#
# Filters.
#--------------------------------------------------------------------------"""


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


"""--------------------------------------------------------------------------#
# Controllers.
#--------------------------------------------------------------------------"""

#  Functions
#  ----------------------------------------------------------------


#  This function validates inputed phone numbers and corrects them to
#  an 123-456-7890 format if entered as all digits.
def format_phone(form_phone):
    if len(form_phone) == 10:
        return (form_phone[:3] + '-' + form_phone[3:6] +
                '-' + form_phone[6:])
    elif ((len(form_phone) < 10 and len(form_phone) > 0) or
          len(form_phone) > 12):
        raise Exception('Phone Error')
    else:
        return form_phone


#  This function returns a single record in Dict format and checks on whether
#  it has a genres attribut that needs to be split into a list.
def getRecordAsDict(table, record_id):
    this_record = table.query.get(record_id)
    if hasattr(this_record, 'genres'):
        this_record.genres = this_record.genres.split(',')
    record_as_dict = this_record.__dict__
    return(record_as_dict)


#  Main
#  ----------------------------------------------------------------

@app.route('/')
def index():
    return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------


#  List Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # Lists venues ordered by city and state.
    error = False
    #  num_shows should be aggregated based on number of upcoming
    # shows per venue.

    try:
        venue_query = (
            Venue.query.with_entities(Venue.id, Venue.name,
                                      Venue.city, Venue.state)
            .order_by(Venue.name).all()
        )

        locations = sorted(list(set([(record.city, record.state) for record
                                in venue_query])), key=lambda x: (x[1], x[0]))
        venue_list = []
        # print(locations)
        for location in locations:
            location_venues = []
            for record in venue_query:
                if record.city == location[0] and (record.state ==
                                                   location[1]):
                    # print(record.city, record.state)
                    location_venues.append({'id': record.id,
                                           'name': record.name})
            venue_list.append({'city': location[0],
                               'state': location[1],
                               'venues': location_venues})
    except Exception as e:
        error = True
        print(sys.exc_info())
        print('Exception', e)
    finally:
        db.session.close()

    if error:
        flash('An error occured. Venues cannot be shown.')
        return redirect(url_for('index'))
    elif venue_list == []:
        flash('The Venues table in the database is empty.')
        return redirect(url_for('index'))
    else:
        return render_template('pages/venues.html', areas=venue_list)


#  Search Venues
#  ----------------------------------------------------------------


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


#  Show Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    error = False
    try:
        this_venue = getRecordAsDict(Venue, venue_id)
    except Exception as e:
        error = True
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Venue with ID ' + str(venue_id) +
              ' could not be displayed.')
        return redirect(url_for('venues'))
    else:
        return render_template('pages/show_venue.html',
                               venue=this_venue)

    #   "past_shows": [{
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [{
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    # Renders the create venue form.
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Adds new venue to database.
    form = VenueForm()
    error = False

    try:
        if not form.validate():
            return render_template('forms/new_venue.html', form=form)

        this_venue = Venue(
                        name=form.name.data.strip(),
                        genres=','.join(form.genres.data),
                        city=form.city.data.strip(),
                        state=form.state.data,
                        address=form.address.data.strip(),
                        phone=format_phone(form.phone.data),
                        image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data,
                        website=form.website.data,
                        seeking_talent=form.seeking_talent.data,
                        seeking_description=form.seeking_description.data
        )

        db.session.add(this_venue)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] +
              ' could not be listed.')
        return render_template('forms/new_venue.html', form=form)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Edit Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # Populates form with venue record from database.
    form = VenueForm()
    error = False

    try:
        this_venue = getRecordAsDict(Venue, venue_id)
    except Exception as e:
        error = True
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Venue with ID ' + str(venue_id) +
              ' could not be edited.')
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        form = VenueForm(data=this_venue)
        return render_template('forms/edit_venue.html', form=form,
                               venue=this_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Edits venue record in database.
    form = VenueForm()
    error = False

    try:
        this_venue = Venue.query.get(venue_id)

        if not form.validate():
            return render_template('forms/edit_venue.html', form=form,
                                   venue=this_venue)

        this_venue.name = form.name.data
        this_venue.genres = ','.join(form.genres.data)
        this_venue.city = form.city.data.strip()
        this_venue.state = form.state.data
        this_venue.address = form.address.data.strip()
        this_venue.phone = format_phone(form.phone.data)
        this_venue.image_link = form.image_link.data
        this_venue.facebook_link = form.facebook_link.data
        this_venue.website = form.website.data
        this_venue.seeking_talent = form.seeking_talent.data
        this_venue.seeking_description = form.seeking_description.data

        db.session.add(this_venue)
        db.session.commit()

    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] +
              ' could not be edited.')
        # return render_template('forms/edit_venue.html', form=form)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Deletes a venue from the database.
    error = False

    try:
        this_venue = Venue.query.get(venue_id)
        this_venue_name = this_venue.name
        db.session.delete(this_venue)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' + this_venue.name +
              ' could not be deleted.')
        return jsonify(success=False), 500
    else:
        flash('Venue ' + this_venue.name + ' was successfully deleted!')

    return jsonify(success=True), 200


#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------


#  List Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Lists artist records in the database.
    error = False

    try:
        artists_query = Artist.query.with_entities(Artist.id,
                                                   Artist.name).all()

        def listArtists(artists_query):
            artist_list = []

            for record in artists_query:
                artist_list.append({
                  "id": record.id,
                  "name": record.name,
                })
            return artist_list

        artist_list = listArtists(artists_query)
    except Exception as e:
        error = True
        print(sys.exc_info())
        print('Exception : ', e)
    finally:
        db.session.close()

    if error:
        flash('An error occured. Artists cannot be shown.')
        return redirect(url_for('index'))
    elif artist_list == []:
        flash('The Artist table in the database is empty.')
        return redirect(url_for('index'))
    else:
        return render_template('pages/artists.html', artists=artist_list)


#  Search Artists
#  ----------------------------------------------------------------


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


#  Show Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    error = False

    try:
        this_artist = getRecordAsDict(Artist, artist_id)
        print(this_artist)
    except Exception as e:
        error = True
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Artist with ID ' + str(artist_id) +
              ' could not be displayed.')
        return redirect(url_for('artists'))
    else:
        return render_template('pages/show_artist.html',
                               artist=this_artist)

#     "past_shows": [{
#       "venue_id": 1,
#       "venue_name": "The Musical Hop",
#       "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 3,
#   }

#   data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=this_artist)


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    # Renders the new artist form.
    form = ArtistForm()
    print("artist page rendered")
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Adds new artist to the database.
    form = ArtistForm()
    error = False
    print("Post happened")
    try:
        if not form.validate():
            print("form not valid")
            return render_template('forms/new_artist.html', form=form)

        this_artist = Artist(
                        name=form.name.data.strip(),
                        genres=','.join(form.genres.data),
                        city=form.city.data.strip(),
                        state=form.state.data,
                        phone=format_phone(form.phone.data),
                        image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data,
                        website=form.website.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data
        )

        db.session.add(this_artist)
        db.session.commit()
        print("RECORD COMMITTED")
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] +
              ' could not be listed.')
        return render_template('forms/new_artist.html', form=form)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Edit Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Populates form with artist record from database.
    form = ArtistForm()
    error = False

    try:
        this_artist = getRecordAsDict(Artist, artist_id)
    except Exception as e:
        error = True
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Artist with ID ' + str(artist_id) +
              ' could not be edited.')
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        form = ArtistForm(data=this_artist)
        return render_template('forms/edit_artist.html', form=form,
                               artist=this_artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Edits venue record in database.
    form = ArtistForm()
    error = False

    try:
        this_artist = Artist.query.get(artist_id)

        if not form.validate():
            return render_template('forms/edit_artist.html', form=form,
                                   venue=this_artist)

        this_artist.name = form.name.data
        this_artist.genres = ','.join(form.genres.data)
        this_artist.city = form.city.data.strip()
        this_artist.state = form.state.data
        this_artist.phone = format_phone(form.phone.data)
        this_artist.image_link = form.image_link.data
        this_artist.facebook_link = form.facebook_link.data
        this_artist.website = form.website.data
        this_artist.seeking_venue = form.seeking_venue.data
        this_artist.seeking_description = form.seeking_description.data

        db.session.add(this_artist)
        db.session.commit()

    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] +
              ' could not be edited.')
        return render_template('forms/edit_artist.html', form=form)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))


#  Delete Artist
#  ----------------------------------------------------------------


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # Deletes an artist from the database.
    error = False

    try:
        this_artist = Artist.query.get(artist_id)
        this_artist_name = this_artist.name
        db.session.delete(this_artist)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' + this_artist.name +
              ' could not be deleted.')
        return jsonify(success=False), 500
    else:
        flash('Artist ' + this_artist.name + ' was successfully deleted!')

    return jsonify(success=True), 200


# -----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

"""--------------------------------------------------------------------------#
# Launch.
#--------------------------------------------------------------------------"""

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
