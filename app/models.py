from app import db

class Venue(db.Model): 
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120)) 
    website = db.Column(db.String(500))
    genres = db.Column('genres', db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(500))  
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref='pVenue', lazy=True, cascade='all, delete')
    
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120)) 
    website = db.Column(db.String(500))
    genres = db.Column('genres', db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(500), nullable=False) 
    image_link = db.Column(db.String(500)) 
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref='pArtist', lazy=True, cascade='all, delete')

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)