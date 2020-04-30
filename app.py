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


# This function returns a list of all shows and returns it
# to the controller for display in the view.
def getShowList():
    show_list = Show.query.all()
    for show in show_list:
        show.venue_name = show.venue.name
        show.artist_name = show.artist.name
        show.artist_image_link = show.artist.image_link
        show.start_time = str(show.start_time)
    return(show_list)


# This function counts the number of shows for
# a record that matches on the ID parameters.
def getShowCount(show_list, match_id, record_id):
    count = 0
    for show in show_list:
        if getattr(show, match_id) == record_id:
            count += 1
    return(count)


# This function returns results filtered by search terms.
def getKeywordResults(table, column, search_term, shows_match_id=None):
    time_now = datetime.now()
    search_result = []
    num_upcoming_shows = None
    search_query = (table.query
                    .filter(column.ilike('%' + search_term + '%')).all()
                    )
    if shows_match_id is not None:
        show_query = Show.query.filter(Show.start_time > time_now).all()

    for result in search_query:
        if shows_match_id is not None:
            num_upcoming_shows = getShowCount(show_query, shows_match_id,
                                              result.id)

        search_result.append({
            "id": result.id,
            "name": result.name,
            **({"num_upcoming_shows": num_upcoming_shows}
                if num_upcoming_shows is not None else{})
        })
    return({
        "count": len(search_query),
        "data": search_result
    })


def getRecentListings():
    recent_artists = []
    recent_venues = []
    recent_artists_query = (
        Artist.query
        .order_by(Artist.id.desc()).limit(5).all()
    )
    recent_venues_query = (
        Venue.query
        .order_by(Venue.id.desc()).limit(5).all()
    )
    for artist in recent_artists_query:
        recent_artists.append({
            'id': artist.id,
            'name': artist.name,
            'image_link': artist.image_link
        })
    for venue in recent_venues_query:
        recent_venues.append({
            'id': venue.id,
            'name': venue.name,
            'image_link': venue.image_link
        })
    return ({
        'artists': recent_artists,
        'num_recent_artists': len(recent_artists_query),
        'venues': recent_venues,
        'num_recent_venues': len(recent_venues_query)
    })


#  ----------------------------------------------------------------
#  Main
#  ----------------------------------------------------------------


@app.route('/')
def index():
    # Displays the home page
    error = False
    recent_listings = []

    try:
        recent_listings = getRecentListings()
    except Exception as e:
        error = True
        print('Exception', e)
    finally:
        db.session.close()

    if error:
        flash('An error occured. Recent listings cannot be shown.')
        return render_template('pages/home.html',
                               recent_listings=recent_listings)
    elif recent_listings == []:
        flash('The does not contain any artists or venues.')
        return render_template('pages/home.html',
                               recent_listings=recent_listings)
    else:
        return render_template('pages/home.html',
                               recent_listings=recent_listings)


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------


#  List venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # Lists venues ordered by city and state.
    error = False
    venue_list = []
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
    # Returns search results for venues on keyword match.
    error = False
    try:
        search_term = request.form.get('search_term', '').strip()
        if search_term == '':
            return redirect(url_for('venues'))
        response = getKeywordResults(Venue, Venue.name, search_term,
                                     shows_match_id='venue_id')
    except Exception as e:
        error = True
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Search could not be completed')
        return redirect(url_for('venues'))
    else:
        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))


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
    return redirect(url_for('index'))


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
        print('Exception: ', e)
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' + this_venue_name +
              ' could not be deleted.')
        return jsonify(success=False), 500
    else:
        flash('Venue ' + this_venue_name + ' was successfully deleted!')

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
    artist_list = []

    try:
        artists_query = Artist.query.with_entities(Artist.id,
                                                   Artist.name).all()

        for record in artists_query:
            artist_list.append({
                "id": record.id,
                "name": record.name,
            })
    except Exception as e:
        error = True
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
    # Returns search results for venues on keyword match.
    error = False
    try:
        search_term = request.form.get('search_term', '').strip()
        if search_term == '':
            return redirect(url_for('artists'))
        response = getKeywordResults(Artist, Artist.name, search_term)
    except Exception as e:
        error = True
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Search could not be completed')
        return redirect(url_for('artists'))
    else:
        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))


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
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name'] +
              ' could not be listed.')
        return render_template('forms/new_artist.html', form=form)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))


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
        print('Exception: ', e)
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' + this_artist_name +
              ' could not be deleted.')
        return jsonify(success=False), 500
    else:
        flash('Artist ' + this_artist_name + ' was successfully deleted!')

    return jsonify(success=True), 200


# -----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------


#  List shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    error = False

    try:
        show_list = getShowList()
    except Exception as e:
        error = True
        print('Exception', e)
    finally:
        db.session.close()

    if error:
        flash('An error occured. Shows cannot be shown.')
        return redirect(url_for('index'))
    elif show_list == []:
        flash('The Show table in the database is empty.')
        return redirect(url_for('index'))
    else:
        return render_template('pages/shows.html', shows=show_list)


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
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
        return render_template('forms/new_show.html', form=form)
    else:
        flash('Show was successfully listed!')
    return redirect(url_for('index'))


#  Edit show
#  ----------------------------------------------------------------


@app.route('/shows/<int:show_id>/edit', methods=['GET'])
def edit_show(show_id):
    # Populates form with show record from database.
    error = False

    try:
        this_show = getRecordAsDict(Show, show_id)
    except Exception as e:
        error = True
        print('Exception: ', e)
    finally:
        db.session.close()
    if error is True:
        flash('An error occurred. Venue with ID ' + str(show_id) +
              ' could not be edited.')
        # return redirect(url_for('show_venue', show_id=show_id))
    else:
        form = ShowForm(data=this_show)
        return render_template('forms/edit_show.html', form=form,
                               show=this_show)


@app.route('/shows/<int:show_id>/edit', methods=['POST'])
def edit_show_submission(show_id):
    # Edits venue record in database.
    form = ShowForm()
    error = False

    try:
        this_show = Show.query.get(show_id)

        if not form.validate():
            return render_template('forms/edit_show.html', form=form,
                                   show=this_show)

        this_show.artist_id = form.artist_id.data
        this_show.venue_id = form.venue_id.data
        this_show.start_time = form.start_time.data

        db.session.add(this_show)
        db.session.commit()

    except Exception as e:
        error = True
        db.session.rollback()
        print('Exception: ', e)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show with ID ' + str(show_id) +
              ' could not be edited.')
    else:
        flash('Show with ID ' + str(show_id) + ' was successfully edited!')
    return redirect(url_for('shows'))


#  Delete show
#  ----------------------------------------------------------------


@app.route('/shows/<show_id>', methods=['DELETE'])
def delete_show(show_id):
    # Deletes a venue from the database.
    error = False
    try:
        this_show = Show.query.get(show_id)
        this_show_id = this_show.id
        db.session.delete(this_show)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print('Exception: ', e)
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Show with ID ' + str(this_show_id) +
              ' could not be deleted.')
        return jsonify(success=False), 500
    else:
        flash('Show with ID ' + str(this_show_id) +
              ' was successfully deleted!')

    return jsonify(success=True), 200


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
        Formatter('%(asctime)s %(levelname)s: %(message)s' +
                  ' [in %(pathname)s:%(lineno)d]')
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
