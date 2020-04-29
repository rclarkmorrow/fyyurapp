"""--------------------------------------------------------------------------#
# Imports
#--------------------------------------------------------------------------"""


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
from models import db, Venue, Artist


"""--------------------------------------------------------------------------#
# App Config.
#--------------------------------------------------------------------------"""

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


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
        raise Exception('Phone validation on the conrollter failed.')
    else:
        return form_phone


#  This function returns a single record in Dict format for display.
def getRecordAsDict(table, record_id):
    time_now = datetime.now()
    this_record = table.query.get(record_id)

    if hasattr(this_record, 'genres'):
        # Conditional that splits genres into a list, if record
        # has the genres attribute.
        this_record.genres = this_record.genres.split(',')

    record_as_dict = this_record.__dict__

    if hasattr(this_record, 'shows'):
        # Conditional returns a list of shows, if record
        # has the shows attribute (NOTE: shows is a DB relationsip).
        shows = (getShows(this_record.shows, time_now))
        record_as_dict.update(shows)

    return(record_as_dict)


# This function loops a record's shows and structures data
# as a list in the format needed for display. (e.g. a list of past
# shows, a list of upcoming shows, and the show counts).
def getShows(show_list, time_now):
    upcoming_shows = []
    past_shows = []

    for show in show_list:
        if show.start_time > time_now:
            upcoming_shows.append({
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': str(show.start_time)
            })
        else:
            past_shows.append({
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': str(show.start_time)
            })

    return ({
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    })


# This function counts the number of shows for
# a record that matches on the ID parameters.
def getShowCount(show_list, match_id, record_id):
    count = 0
    for show in show_list:
        if getattr(show, match_id) == record_id:
            count += 1
    return(count)


#  ----------------------------------------------------------------
#  Main
#  ----------------------------------------------------------------

@app.route('/')
def index():
    return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------


#  List venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # Lists venues ordered by city and state.
    error = False

    try:
        # Sets a single time as now for all time based logic
        time_now = datetime.now()
        # Single query gets necessary venue information to avoid multiple
        # queries in loops.
        venue_query = (
            Venue.query.with_entities(Venue.id, Venue.name,
                                      Venue.city, Venue.state)
            .order_by(Venue.name).all()
        )
        # Single query to return show all future show records to avoid multiple
        # queries in loops.
        show_query = Show.query.filter(Show.start_time > time_now).all()

        locations = sorted(list(set([(record.city, record.state) for record
                                in venue_query])), key=lambda x: (x[1], x[0]))
        venue_list = []

        for location in locations:
            location_venues = []

            for record in venue_query:

                if record.city == location[0] and (record.state ==
                                                   location[1]):

                    num_shows = getShowCount(show_query, 'venue_id',
                                             record.id)

                    location_venues.append({
                        'id': record.id,
                        'name': record.name,
                        'num_upcoming_shows': num_shows
                    })

            venue_list.append({
                'city': location[0],
                'state': location[1],
                'venues': location_venues
            })
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


#  Search venues
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


#  Show venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Shows the venue page with the given venue_id
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


#  Create venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    # Renders the create venue form.
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Adds new venue record to database.
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


#  Edit venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # Populates form with venue record from database.
    error = False

    try:
        this_venue = getRecordAsDict(Venue, venue_id)
    except Exception as e:
        error = True
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
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete venue
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


#  List artists
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


#  Search artists
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


#  Create artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    # Renders the new artist form.
    form = ArtistForm()
    print("artist page rendered")
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Adds new artist record to the database.
    form = ArtistForm()
    error = False
    try:
        if not form.validate():
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


#  Edit artist
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
                                   artist=this_artist)

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
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))


#  Delete artist
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


#  List shows
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


#  Create show
#  ----------------------------------------------------------------


@app.route('/shows/create')
def create_shows():
    # Renders the new show form.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Creates new show record in the database.
    form = ShowForm()
    error = False
    try:
        if not form.validate():
            print("New Show Not Validate")
            return render_template('forms/new_show.html', form=form)

        this_show = Show(
                        artist_id=form.artist_id.data,
                        venue_id=form.venue_id.data,
                        start_time=form.start_time.data,
        )

        db.session.add(this_show)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
        return render_template('forms/new_show.html', form=form)
    else:
        flash('Show was successfully listed!')
    return render_template('pages/home.html')


# -----------------------------------------------------------------
#  Error handlers
#  ----------------------------------------------------------------


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
