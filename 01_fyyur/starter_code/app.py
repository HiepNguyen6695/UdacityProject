#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import backref
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form

from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# Connected successfully to a local postgresql database in config.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:Crystallam1!@localhost:5432/project1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.from_object('config')
db = SQLAlchemy(app)

#Implemented a database migration using Flask-Migrate
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  # Create a different name for venue
  __tablename__ = 'venues'

  # Create attributes for venue
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  seeking_description = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  
  # Many-to-many relationship is set a connection between Artist and Show table.
  artists = db.relationship('Artist', secondary='shows')
  shows = db.relationship('Show',lazy='dynamic', backref=('venues'), cascade="all,delete")

  # Return all of the necessary info from Venue table
  def show_venue_info(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'address': self.address,
      'phone': self.phone,
      'genres': self.genres,
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website': self.website,
      #'seeking_talent': self.seeking_talent,
      'seeking_description': self.seeking_description,
    }

    # Print out the console.
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
  # Create a different name for artist
  __tablename__ = 'artists'

  # Create attributes for artist
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_description = db.Column(db.String(120))

  # Many-to-many relationship is set a connection between Venue and Show table.
  venues = db.relationship('Venue', secondary='shows')
  shows = db.relationship('Show',lazy='dynamic', backref=('artists'),cascade="all,delete")

  # Return all of the necessary info from Artist table
  def show_artist_info(self):
    return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        #'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
    }
        
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=True)
  start_time = db.Column(db.DateTime, nullable=True)

  venue = db.relationship('Venue')
  artist = db.relationship('Artist')

   # Return all of the references from Artist table
  def show_artist_info(self):
    return{
      'artist_id': self.artist_id,
      'artist_name': self.artists.name,
      'artist_image_link': self.artists.image_link,
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') # Send the parse of the start_time
    }

  # Return all of the references from Venue table
  def show_venue_info(self):
    return{
      'venue_id': self.venue_id,
      'venue_name': self.venue,
      'venue_image_link': self.venue.image_link,
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') # Send the parse of the start_time
    }

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Route to home page.
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

# View info from database to venue page.
@app.route('/venues')
def venues():
  # Get all of the info grouped by venue's id, state, and city.
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()

  # Initialize some variables.
  venue_state_and_city = ''
  data = []
  pre_city = None
  pre_state = None
  
  # Loop all of the venue's data
  for venue in venues:
    # Set the current time for each data
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')

    # Filter the upcoming show from venue's and show's relationship.
    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()

    if venue_state_and_city == venue.city + venue.state and venue.city == pre_city and venue.state == pre_state:
      data["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(upcoming_shows) # Push number of upcoming shows into data variable.
      })
    else:
      if venue_state_and_city != venue.city + venue.state:
        temp = {
          "city":venue.city,
          "state":venue.state,
          "venues": [{
            "id": venue.id,
            "name":venue.name,
            "num_upcoming_shows": len(upcoming_shows)  # Push number of upcoming shows into temp variable.
          }]
        }
      pre_city = venue.city # If there are previous cities, return these cities.
      pre_state = venue.state # If there are previous states, return these states.
      data.append(temp)

  return render_template('pages/venues.html', areas=data)

# Search each venue with case-intensive term.
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Find terms when users type in a search_term field.
  search_term = request.form.get('search_term')

  # Get info from a search_term field to find the info in the database.
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []

  # Get the data from venue by looping through every data in the database.
  for venue in venues:
    tmp = {}
    
    tmp['id'] = venue.id
    tmp['name'] = venue.name
    data.append(tmp) # Push all of the info into data variables.

  # Response to the view
  response = {}
  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


# View each of the venues that exist in the View.
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)

  # Use Anomyous to find the previous and upcoming time in the database.
  # Sort through the show table with many-to-many relationship between show and venue.
  pre_shows_time = filter(lambda x: x.start_time < datetime.today(), venue.shows)
  upcoming_shows_time = filter(lambda x: x.start_time >= datetime.today(), venue.shows)

  # Set all the time out.
  pre_shows_time_set = list(pre_shows_time) 
  upcoming_shows_time_set = list(upcoming_shows_time)

  # Find these shows with time set in the show table.
  map_pre_shows = map(lambda x: x.show_artist_info(), pre_shows_time_set)
  map_upcoming_shows = map(lambda x: x.show_artist_info(), upcoming_shows_time_set)

  # Set all of the shows
  pre_shows = list(map_pre_shows)
  upcoming_shows = list(map_upcoming_shows)

  # Get data from venue
  data = venue.show_venue_info()

  # Put all of the needed info into data variable.
  data['past_shows'] = pre_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(pre_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

# Create some forms for venue page.
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  # Get form from VenueForm object.
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# Create venue page with information from venue table.
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Insert data into the database.
  form = VenueForm(request.form)

  # Get information from users
  try:
    venue = Venue()
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website.data

    # Add all of the info in the database.
    db.session.add(venue)

    # Save all of that info.
    db.session.commit()

    # On successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    # If something happens, then return to the beginning.
    db.session.rollback()

    # Print error.
    print(sys.exc_info())

    # On unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    # After insertion, close the database.
    db.session.close()
  return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
# Show Artist's info on the artist page.
@app.route('/artists')
def artists():
  # Get all of the artist info.
  artist = Artist.query.all()
  return render_template('pages/artists.html', artists=artist)

# Search any artists.
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Get information from the search term field.
  search_term = request.form.get('search_term')

  # Get info in the database by using terms from a search term field.
  result = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  # Add info to a dictionary.
  response = {}
  response['count'] = len(result)
  response['data'] = result
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# View each artist's info when user click on their name.
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)

  # Use Anomyous to find the previous and upcoming time in the database.
  # Sort through the show table with many-to-many relationship between show and artist table.
  pre_shows_time = filter(lambda x: x.start_time < datetime.today(), artist.shows)
  upcoming_shows_time = filter(lambda x: x.start_time >= datetime.today(), artist.shows)

  # Set all the time out.        
  pre_shows_time_set = list(pre_shows_time) 
  upcoming_shows_time_set = list(upcoming_shows_time)

  # Find these shows with time set in the show table.
  map_pre_shows = map(lambda x: x.show_venue_info(), pre_shows_time_set)
  map_upcoming_shows = map(lambda x: x.show_venue_info(), upcoming_shows_time_set)

  # Set all of the shows
  pre_shows = list(map_pre_shows)
  upcoming_shows = list(map_upcoming_shows)

  # Get data from artist
  data = artist.show_artist_info()

  # Put all of the needed info into data variable.
  data['past_shows'] = pre_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(pre_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.website = form.website.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully updated!')
  except:
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
# Create some forms for artist page.
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # Get forms from form.py and put on artist page.
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# Create artist info page.
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Insert data into the database.
  form = ArtistForm(request.form)

  # Put artist's info into the database.
  try:
    artist = Artist()
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_description = form.seeking_description.data

    # Add info in the database.
    db.session.add(artist)

    # Save info in the database.
    db.session.commit()

    # On successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    # If error occurs, return back to the beginning.
    db.session.rollback()

    # Print out errors.
    print(sys.exc_info())

    # On unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    # After insertion, close the database.
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
# View info to show page.
@app.route('/shows')
def shows():
  # Get all of the possible info in Show table.
  shows = Show.query.all()

  # Initialize array.
  data = []

  # Loop through each show's info and put them in names of a dictionary.
  for show in shows:
    # Add those info in the array.
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })

  return render_template('pages/shows.html', shows=data)

# Show on the show page.
@app.route('/shows/create')
def create_shows():
  # Get some forms in the forms.py
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# Create info in the show table.
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # Get some info from form.py.
  form = ShowForm(request.form)

  # Add data into show table.
  try:
    show = Show()
    show.artist_id = form.artist_id.data
    show.venue_id = form.venue_id.data
    show.start_time = form.start_time.data

    # Add info in the database.
    db.session.add(show)

    # Save info in the database.
    db.session.commit()

    # On successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # If an error occurs, roll back to where it begins.
    db.session.rollback()

    # Print out the error.
    print(sys.exc_info()) 

    # On unsuccessful db insert, flash an error instead.
    flash('Show was not successfully listed!')

  finally:
    # After insertion, close the database.
    db.session.close()
    
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Error
#----------------------------------------------------------------------------#

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
