#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from flask_babel import Babel
from flask_migrate import Migrate
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db, compare_type=True)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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

#List of all venues
@app.route('/venues')
def venues():
    result = []
    #distinct city and state
    locations = Venue.query.distinct('city','state').all()

    for loc in locations:
      venues = Venue.query.filter(Venue.city == loc.city, Venue.state == loc.state).all()
      record = {
        'city': loc.city,
        'state': loc.state,
        'venues': venues,
      }
      result.append(record)

    return render_template('pages/venues.html', areas=result)

#search venues with partial string search and case-insensitive.
@app.route('/venues/search', methods=['POST'])    #num_upcoming_shows left
def search_venues():
    # main.html -> name="search_term"
    search_term = request.form.get('search_term', '')
    data = []
    counter = 0

    #ILIKE allows you to perform case-insensitive pattern matching
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all() 
    for result in results:
        counter += 1
        data.append({"id": result.id, "name": result.name})

    response={ "count": counter, "data": data }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# show venue page with the given venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id = venue_id).all()
    upcoming_shows = []
    past_shows = []
    upcoming_shows_count = 0
    past_shows_count = 0

    current_time = datetime.datetime.now()
    
    for show in shows:
        if show.start_time >= current_time:
            upcoming_shows_count += 1
            record = {
              "artist_id": show.artist_id,
              "artist_name": Artist.query.get(show.artist_id).name,
              "artist_image_link": Artist.query.get(show.artist_id).image_link,
              "start_time": str(show.start_time),
            }
            upcoming_shows.append(record)
        else:
            past_shows_count += 1
            past_show_record = {
              "artist_id": show.artist_id,
              "artist_name": Artist.query.get(show.artist_id).name,
              "artist_image_link": Artist.query.get(show.artist_id).image_link,
              "start_time": str(show.start_time),
            }
            past_shows.append(past_show_record)
    
    data = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    return render_template('pages/show_venue.html', venue=data)
       

#  Create and Delete Venues
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

# Create venue
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
      error = False
      try:
          name = form.name.data
          city = form.city.data
          state = form.state.data
          address = form.address.data
          phone = form.phone.data
          website = form.website.data
          genres = form.genres.data
          image_link = form.image_link.data
          facebook_link = form.facebook_link.data
   
          seeking_description = form.seeking_description.data
          if seeking_description:
            seeking_talent = True
          else:
            seeking_talent = False

          venue = Venue(name=name, city=city, state=state,
                        address=address, phone=phone, image_link=image_link,
                        facebook_link=facebook_link, website=website, genres=genres,
                        seeking_talent=seeking_talent, seeking_description=seeking_description)

          db.session.add(venue)
          db.session.commit()
      except Exception as e:
          error = True
          db.session.rollback()
          print(f'Error ==> {e}')
      finally:
          db.session.close()
      if error:
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Venue ' +
                request.form['name'] + ' could not be listed.')
      else:
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      errors_list = []
      for error in form.errors.values():
        errors_list.append(error[0])
      flash('Invalid submission: \n' + ', '.join(errors_list))
      return render_template('forms/new_venue.html', form=form)

    return render_template('pages/home.html')

# Delete venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
# TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venues = Venue.query.get(venue_id)
    name = venues.name
    db.session.delete(venues)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Error ==> {e}')
  finally:
    db.session.close()

  if error:
    flash('Error)')
  else:
    flash('Venue ' +name+' deleted.')
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
  return 'OK'



#  Artists
#  ----------------------------------------------------------------

#List of all artists alphabitacly 
@app.route('/artists')
def artists():
  result = []

  artists = Artist.query.order_by(Artist.name).all()

  for artist in artists:
    result.append({"id": artist.id,"name": artist.name})

  return render_template('pages/artists.html', artists=result)

# search arists
@app.route('/artists/search', methods=['POST'])
def search_artists():
    # main.html -> name="search_term"
    search_term = request.form.get('search_term', '')
    data = []
    counter = 0

    #ILIKE allows you to perform case-insensitive pattern matching
    results = Artist.query.filter(Venue.name.ilike(f'%{search_term}%')).all() 
    for result in results:
        counter += 1
        data.append({"id": result.id, "name": result.name})

    response={ "count": counter, "data": data }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# show artist
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id = artist_id).all()
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    current_time = datetime.datetime.now()

    for show in shows:
        if(show.start_time >= current_time):
            upcoming_shows_count+=1
            upcoming_shows.append({
              "venue_id": show.venue_id,
              "venue_name": Venue.query.get(show.venue_id).name,
              "venue_image_link": Venue.query.get(show.venue_id).image_link,
              "start_time": str(show.start_time)
            })
        else:
            past_shows.append({
              "venue_id": show.venue_id,
              "venue_name": Venue.query.get(show.venue_id).name,
              "venue_image_link": Venue.query.get(show.venue_id).image_link,
              "start_time": str(show.start_time)
            })
            past_shows_count+=1

    data={
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
        }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
#edit artist show fields
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)

#edit artist submit fields
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
   
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    if form.validate_on_submit():
      error = False
      try:
        artist.name=form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.genres=form.genres.data
        artist.website=form.website.data
        artist.facebook_link=form.facebook_link.data
        artist.image_link=form.image_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        db.session.add(artist)
        db.session.commit()
      except Exception as e:
        error = True
        db.session.rollback()
        print(f'Error ==> {e}')
      finally:
        db.session.close()
      if error:
        flash('Artist ' + request.form['name'] + ' was not updated.')
      else:
        flash('Artist ' +request.form['name'] + ' was successfully updated.')
    else:
      errors_list = []
      for error in form.errors.values():
        errors_list.append(error[0])
      flash('Invalid submission: \n' + ', '.join(errors_list))
      return render_template('forms/edit_artist.html', form=form, artist=artist)

    return redirect(url_for('show_artist', artist_id=artist_id))


#edit venue show fields
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

#edit venue submit
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form)
    if form.validate_on_submit():
      try:
        venue.name=form.name.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.address=form.address.data
        venue.phone=form.phone.data
        venue.genres=form.genres.data
        venue.facebook_link=form.facebook_link.data
        venue.image_link=form.image_link.data
        venue.website=form.website.data

        venue.seeking_description=form.seeking_description.data
        if venue.seeking_description:
          venue.seeking_talent = True
        else:
          venue.seeking_talent = False
        
        db.session.add(venue)
        db.session.commit()
      except Exception as e:
        error = True
        db.session.rollback()
        print(f'Error ==> {e}')
      finally:
        db.session.close()
      if error:
        flash('Error! Venue ' + request.form['name'] + ' was not updated.')
      else:
        flash( 'Venue ' + request.form['name'] + ' was successfully updated.')
    else:
      errors_list = []
      for error in form.errors.values():
        errors_list.append(error[0])
      flash('Invalid submission: \n' + ', '.join(errors_list))
      return render_template('forms/edit_venue.html', form=form)

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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm()
    if form.validate_on_submit():
      error = False
      try:
          name = form.name.data
          city = form.city.data
          state = form.state.data
          phone = form.phone.data
          genres = form.genres.data
          website = form.website.data
          image_link = form.image_link.data
          facebook_link = form.facebook_link.data

          seeking_description = form.seeking_description.data
          if seeking_description:
            seeking_venue = True
          else:
            seeking_venue = False

          artist = Artist(name=name, city=city, state=state,
                            phone=phone, genres=genres, image_link=image_link, website=website,
                            facebook_link=facebook_link, seeking_venue=seeking_venue,
                            seeking_description=seeking_description)

          db.session.add(artist)
          db.session.commit()
      except Exception as e:
          error = True
          db.session.rollback()
          print(f'Error ==> {e}')
      finally:
          db.session.close()
      if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      errors_list = []
      for error in form.errors.values():
        errors_list.append(error[0])
      flash('Invalid submission: \n' + ', '.join(errors_list))
      return render_template('forms/new_artist.html', form=form)

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

#list of all shows
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    
    #by date
    data = []

    shows = Show.query.order_by('start_time').all()
    
    for show in shows:
      record = {
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "artist_id":show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      }
      data.append(record)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

#create show
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    if form.validate_on_submit():
      error = False
      try:
          artist_id = form.artist_id.data
          venue_id = form.venue_id.data
          start_time = form.start_time.data
          show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
          db.session.add(show)
          db.session.commit()
      except Exception as e:
          error = True
          db.session.rollback()
          print(f'Error ==> {e}')
      finally:
          db.session.close()
      if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be saved.')
      else:
        flash('Show was successfully saved.')
    else:
      errors_list = []
      for error in form.errors.values():
        errors_list.append(error[0])
      flash('Invalid submission: \n' + ', '.join(errors_list))
      return render_template('forms/new_show.html', form=form)

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
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
