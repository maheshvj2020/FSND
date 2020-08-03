#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import date
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from domain import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate=Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres= db.Column(db.String)
    seeking_talent=db.Column(db.String)
    seeking_description=db.Column(db.String)
    website=db.Column(db.String)
    shows = db.relationship("Show")


class Artist(db.Model):

    id = db.Column(db.Integer, primary_key=True )
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue=db.Column(db.String)
    seeking_description=db.Column(db.String)
    website=db.Column(db.String)
    shows = db.relationship("Show")
   
# TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  id = db.Column(db.Integer, primary_key=True,autoincrement=True)
  start_time = db.Column(db.String(120),nullable=False)
  venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  venue = db.relationship("Venue"  ,backref="show",lazy=True)
  artist = db.relationship("Artist", backref="show",lazy=True)

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#-mc-  shows model
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

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venue_list=Venue.query.order_by(Venue.city,Venue.state).all()
  data=[]
  index=0
  venues=[]
  city=''
  state=''
  # Logic for grouping venues based on city and state
  for venue in venue_list:
    num_upcoming_shows=0
    for show in venue.shows:
       start_date = dateutil.parser.parse(show.start_time)
       # Comparing show start date with todays date to get upcomming show count
       today= start_date.today()
       if today < start_date:
            num_upcoming_shows+=1
    if(index==0):
       city=venue.city
       state=venue.state
    index+=1   
    if(venue.city==city and venue.state==state ):
       venues.append(SearchResultDataDTO(venue.id,venue.name,num_upcoming_shows))
    else:
       data.append(VenueSearchResultDTO(city,state,venues))
       city=venue.city
       state=venue.state 
       venues=[]
       venues.append(SearchResultDataDTO(venue.id,venue.name,num_upcoming_shows))   
  if(len(venues)>0):
    data.append(VenueSearchResultDTO(city,state,venues))
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  search = "%{}%".format(search_term)
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  count=len(venues)
  res_data=[]
  for venue in venues:
    show_count=0 
    for show in venue.shows:
          start_date = dateutil.parser.parse(show.start_time)
          today= start_date.today()
          # Comparing show start date with todays date to get upcomming show count
          if today < start_date:
            show_count+=1
    res=SearchResultDataDTO(venue.id,
    venue.name,show_count)
    res_data.append(res)
  response=SearchResultDTO(count,res_data)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  past_shows=[]
  upcoming_shows=[]
  for show in venue.shows:
          start_date = dateutil.parser.parse(show.start_time)
          today= start_date.today()
          # Comparing show start date with todays date to get upcomming and past shows 
          if today < start_date:
            upcoming_shows.append(ShowArtistDTO(show.artist_id,show.artist.name,
            show.artist.image_link,show.start_time))           
          else:
            past_shows.append(ShowArtistDTO(show.artist_id,show.artist.name,
            show.artist.image_link,show.start_time)) 
  past_show_count=len(past_shows)
  upcoming_show_count=len(upcoming_shows)
  data=VenueResultDTO(venue.id,venue.name,venue.genres.split(","),venue.address,venue.city,venue.state,
  venue.phone,venue.website,venue.facebook_link,venue.image_link,venue.seeking_talent,venue.seeking_description,
  past_shows,upcoming_shows,past_show_count,upcoming_show_count)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = ",".join(request.form.getlist('genres'))
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    venue = Venue(name=name, city=city,state=state,address=address,phone=phone,
    image_link=image_link,genres=genres,facebook_link=facebook_link,website=website,
    seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  redirect_method=''
  try:
    venue = Venue.query.get(venue_id)
    if(len(venue.shows)>0):
     flash('Venue ' + venue.name + ' could not be deleted!.\n Associated shows found')
     redirect_method='show_venue'
    else:
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully deleted!')
      redirect_method='index'
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for(redirect_method, venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[]
  for artist in artists:
    data.append({"id":artist.id,"name":artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  search = "%{}%".format(search_term)
  artists = Artist.query.filter(Artist.name.ilike(search)).all()
  count=len(artists)
  res_data=[]
  for artist in artists:
    show_count=0 
    for show in artist.shows:
         date = dateutil.parser.parse(show.start_time)
         today= date.today()
         if today < date:
             show_count+=1
    res=SearchResultDataDTO(artist.id,
    artist.name,show_count)
    res_data.append(res)
  response=SearchResultDTO(count,res_data)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  past_shows=[]
  upcoming_shows=[]
  for show in artist.shows:
          start_date = dateutil.parser.parse(show.start_time)
          today= start_date.today()
          if today < start_date:
            upcoming_shows.append(ShowVenueDTO(show.venue_id,show.venue.name,
            show.venue.image_link,show.start_time))           
          else:
            past_shows.append(ShowVenueDTO(show.venue_id,show.venue.name,
            show.venue.image_link,show.start_time)) 
  past_show_count=len(past_shows)
  upcoming_show_count=len(upcoming_shows)
  data=ArtistResultDTO(artist.id,artist.name,artist.genres.split(","),artist.city,artist.state,
  artist.phone,artist.website,artist.facebook_link,artist.image_link,artist.seeking_venue,artist.seeking_description,
  past_shows,upcoming_shows,past_show_count,upcoming_show_count)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
 
  form.name.data=artist.name
  form.genres.data=artist.genres.split(",")
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.website.data=artist.website
  form.facebook_link.data=artist.facebook_link
  form.seeking_venue.data=artist.seeking_venue
  form.seeking_description.data=artist.seeking_description
  form.image_link.data=artist.image_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist_res = Artist.query.get(artist_id)
    artist_res.name = request.form.get('name')
    artist_res.city = request.form.get('city')
    artist_res.state = request.form.get('state')
    artist_res.phone = request.form.get('phone')
    artist_res.image_link = request.form.get('image_link')
    artist_res.genres = ','.join(request.form.getlist('genres'))
    artist_res.facebook_link = request.form.get('facebook_link')
    artist_res.website = request.form.get('website')
    artist_res.seeking_venue = request.form.get('seeking_venue')
    artist_res.seeking_description = request.form.get('seeking_description')
    db.session.add(artist_res)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   flash('An error occurred. Artist ' + request.form['name'] + ' could not be modified.')
  else:
     flash('Artist ' + request.form['name'] + ' was successfully modified!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_res = Venue.query.get(venue_id)
  venue=VenueResultDTO(venue_res.id,venue_res.name,venue_res.genres.split(","),venue_res.address,venue_res.city,venue_res.state,
  venue_res.phone,venue_res.website,venue_res.facebook_link,venue_res.image_link,venue_res.seeking_talent,venue_res.seeking_description,
  '','','','')
  form.name.data=venue.name
  form.genres.data=venue.genres
  form.address.data=venue.address
  form.city.data=venue.city
  form.state.data=venue.state
  form.phone.data=venue.phone
  form.website.data=venue.website
  form.facebook_link.data=venue.facebook_link
  form.seeking_talent.data=venue.seeking_talent
  form.seeking_description.data=venue.seeking_description
  form.image_link.data=venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue_res = Venue.query.get(venue_id)
    venue_res.name = request.form.get('name')
    venue_res.city = request.form.get('city')
    venue_res.state = request.form.get('state')
    venue_res.address = request.form.get('address')
    venue_res.phone = request.form.get('phone')
    venue_res.image_link = request.form.get('image_link')
    venue_res.genres = ",".join(request.form.getlist('genres'))
    venue_res.facebook_link = request.form.get('facebook_link')
    venue_res.website = request.form.get('website')
    venue_res.seeking_talent = request.form.get('seeking_talent')
    venue_res.seeking_description = request.form.get('seeking_description')
    db.session.add(venue_res)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be modified.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully modified!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = ','.join(request.form.getlist('genres'))
    print('inside artist create post',genres)
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    artist = Artist(name=name, city=city,state=state,phone=phone,image_link=image_link,genres=genres,facebook_link=facebook_link,
    website=website,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
 
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    redirect_method=''
    try:
      artist = Artist.query.get(artist_id)
      if(len(artist.shows)>0):
        flash('Artist ' + artist.name + ' could not be deleted!.\n Associated shows found')
        redirect_method='show_artist'
      else:
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully deleted!')
        redirect_method='index'
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist ' + artist.name + ' could not be deleted.')
  
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for(redirect_method, artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  list=Show.query.all()
  print('res_data_list',list)
  res_data=[]
  for show in list:
    res=ShowsDTO(show.venue_id,
    show.venue.name,show.artist_id,
    show.artist.name,show.artist.image_link,show.start_time)
    res_data.append(res)

  return render_template('pages/shows.html', shows=res_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    start_time = request.form.get('start_time')
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    show = Show(start_time=start_time, artist_id=artist_id,venue_id=venue_id)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
   flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    print(error)
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
