# Benjamin Ferkol
# Fyuur app.py
# April 13, 2021
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from itertools import groupby
import sys
import os
import traceback
from sqlalchemy.orm.exc import NoResultFound


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
db.init_app(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# TO_DO: connect to a local postgresql database DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TO_DO: implement any missing fields, as a database migration using Flask-Migrate DONE
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TO_DO: implement any missing fields, as a database migration using Flask-Migrate DONE
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

# TO_DO Implement Show and Artist models, and complete all model relationships and properties, 
# as a database migration. DONE
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TO_DO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue. DONE
    # query all venues and order results by state and city.
    data = []
    unique_city_state = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    for city_state in unique_city_state:
        venues = Venue.query.filter_by(city=city_state[0], state=city_state[1]).all()
        data.append({
            "city": city_state[0],
            "state": city_state[1],
            "venues": venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TO_DO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" DONE
    search_term = request.form.get('search_term', None)
    data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    count_venues = len(data)
    response = {'data': data, 'count': count_venues}

    return render_template('pages/search_venues.html', results=response,
                            search_term=request.form.get('search_term', ''))
 

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TO_DO: replace with real venue data from the venues table, using venue_id
    data = Venue.query.get(venue_id)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TO_DO: insert form data as a new Venue record in the db, instead DONE
    venue_form = VenueForm(request.form)

    # TO_DO: modify data to be the data object returned from db insertion DONE
    try:
        new_venue = Venue(
            name = venue_form.name.data,
            genres = ','.join(venue_form.genres.data),
            address = venue_form.address.data,
            city = venue_form.city.data,
            state = venue_form.state.data,
            phone = venue_form.phone.data,
            facebook_link = venue_form.facebook_link.data,
            image_link = venue_form.image_link.data)

        db.session.add(new_venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

        # TO_DO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ = DONE
    except Exception as ex:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        traceback.print_exc()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TO_DO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. DONE
    try:
        venue_to_delete = Venue.query.filter(Venue.id == venue_id).one()
        venue_to_delete.delete()
        flash("Venue {0} has been deleted successfully".format(venue_to_delete[0]['name']))
    except NoResultFound:
        abort(404)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TO_DO: replace with real data returned from querying the database = DONE
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TO_DO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band". = DONE
    search_term = request.form.get('search_term', '')
    data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    count = len(data)
    response = {'data': data, 'count': count}

    return render_template('pages/search_artists.html', results=response,
                          search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TO_DO: replace with real artist data from the artist table, using artist_id = DONE
    data = Artist.query.get(artist_id)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TO_DO: populate form with fields from artist with ID <artist_id> = DONE
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.phone.data = artist.phone
    form.city.data = artist.city
    form.state.data = artist.state
    form.facebook_link.data = artist.facebook_link
    form.genres.data = artist.genres

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TO_DO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes = DONE
    form = ArtistForm(request.form)
    try:
        artist = Artist.query.filter_by(id=artist_id).one()
        artist.name = form.name.data,
        artist.genres = json.dumps(form.genres.data),  # array json
        artist.city = form.city.data,
        artist.state = form.state.data,
        artist.phone = form.phone.data,
        artist.facebook_link = form.facebook_link.data,
        artist.image_link = form.image_link.data,

        artist.update()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as exception:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be edited.')

    return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # TO_DO: populate form with values from venue with ID <venue_id> = DONE
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TO_DO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes = DONE
    form = VenueForm(request.form)
    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        venue.name = form.name.data,
        venue.city = form.city.data,
        venue.state = form.state.data,
        venue.address = form.address.data,
        venue.phone = form.phone.data,
        venue.genres = json.dumps(form.genres.data),
        venue.facebook_link = form.facebook_link.data

        venue.update()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    except Exception as exception:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be edited.')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TO_DO: insert form data as a new Venue record in the db, instead = DONE
    artist_form = request.form
    try:
        new_artist = Artist(
            name = artist_form.name.data,
            genres = ','.join(artist_form.genres.data),
            address = artist_form.address.data,
            city = artist_form.city.data,
            state = artist_form.state.data,
            phone = artist_form.phone.data,
            facebook_link = artist_form.facebook_link.data,
            image_link = artist_form.image_link.data)

        # TO_DO: modify data to be the data object returned from db insertion = DONE
        new_artist.add()
  
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # TO_DO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.') = DONE
    except Exception as exception:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TO_DO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue. = DONE
    shows = Show.query.all()
    data = [show.jsonify_artist_venue for show in shows]

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()

    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TO_DO: insert form data as a new Show record in the db, instead = DONE
    show_form = request.form
    try:
        new_show = Show(
        artist_id = show_form.artist_id.data,
        venue_id = show_form.venue_id.data,
        start_time = show_form.start_time.data)

        new_show.update()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TO_DO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ = DONE
    except Exception as exception:
        flash('An error occurred. Show ' +
              request.form['name'] + ' could not be listed.')

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
