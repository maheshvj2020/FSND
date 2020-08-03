
# Objects to format response

class ShowsDTO(object):
    def __init__(self, venue_id, venue_name,artist_id,artist_name,img_url,start_time):
        self.venue_id=venue_id
        self.venue_name=venue_name
        self.artist_id=artist_id
        self.artist_name=artist_name
        self.artist_image_link=img_url
        self.start_time=start_time

class ShowVenueDTO(object):      
    def __init__(self, venue_id, venue_name,img_url,start_time):
            self.venue_id=venue_id
            self.venue_name=venue_name
            self.venue_image_link=img_url
            self.start_time=start_time  


class ShowArtistDTO(object): 
    def __init__(self,artist_id,artist_name,img_url,start_time):
            self.artist_id=artist_id
            self.artist_name=artist_name
            self.artist_image_link=img_url
            self.start_time=start_time    


class VenueResultDTO(object): 
    def __init__(self,id,name,genres,address,city,state,phone,website,facebook_link,image_link,
    seeking_talent,seeking_description,past_shows,upcoming_shows,past_shows_count,upcoming_shows_count):
            self.id=id
            self.name=name
            self.genres=genres
            self.address=address   
            self.city=city
            self.state=state
            self.phone=phone
            self.website=website
            self.facebook_link=facebook_link
            self.image_link=image_link
            self.seeking_talent=seeking_talent
            self.seeking_description=seeking_description
            self.past_shows=past_shows 
            self.upcoming_shows=upcoming_shows
            self.past_shows_count=past_shows_count
            self.upcoming_shows_count=upcoming_shows_count   

class ArtistResultDTO(object): 
    def __init__(self,id,name,genres,city,state,phone,website,facebook_link,image_link,
    seeking_venue,seeking_description,past_shows,upcoming_shows,past_shows_count,upcoming_shows_count):
            self.id=id
            self.name=name
            self.genres=genres 
            self.city=city
            self.state=state
            self.phone=phone
            self.website=website
            self.facebook_link=facebook_link
            self.image_link=image_link
            self.seeking_venue=seeking_venue
            self.seeking_description=seeking_description
            self.past_shows=past_shows 
            self.upcoming_shows=upcoming_shows
            self.past_shows_count=past_shows_count
            self.upcoming_shows_count=upcoming_shows_count              


class SearchResultDTO(object): 
    def __init__(self,count,data):
            self.count=count
            self.data=data 

class SearchResultDataDTO(object): 
    def __init__(self,id,name,num_upcoming_shows):
            self.id=id
            self.name=name
            self.num_upcoming_shows=num_upcoming_shows   

class VenueSearchResultDTO(object): 
    def __init__(self,city,state,venues):
            self.city=city
            self.state=state
            self.venues=venues  

class ArtistSearchResultDTO(object): 
    def __init__(self,city,state,venues):
            self.city=city
            self.state=state
            self.venues=venues  



