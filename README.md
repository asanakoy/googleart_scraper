## Google art project scraper
This is a scrapy crawler for [Google art](https://www.google.com/culturalinstitute/beta/u/0/)  
Use it at your own risk to be banned by google.  
Scrape politely.


<img src="https://lh6.ggpht.com/lKBIJTbW-2EqpF6plsFdNzx1YXyP-5UyF3ug3fPhft2BZYshbva9Klrvp4L0LRg" alt="van Gogh,
   Self-Portrait" title="van Gogh, 
   Self-Portrait" height="347" /> <img src="https://lh6.ggpht.com/KS0tpjUXsHhaL-v_-10dDtQ0RXH81FhRAPxyHgKE-E2jhoM2km_w8g" alt="van Gogh,
   Portrait of Joseph Roulin" title="van Gogh, 
   Portrait of Joseph Roulin" height="347" />
   
   

### Description
The crawler does:
1. Parses [list of artists page](https://www.google.com/culturalinstitute/beta/u/0/category/artist).
2. Parses pages for every individual artist, extracting info about them. For ex.:
   [Rembrandt](https://www.google.com/culturalinstitute/beta/u/0/entity/m0bskv2?categoryId=artist).
3. Extracts a list of artworks for every artist, download images at max resolution 512x512.
4. Parses pages for every individual artwork, extracting info about them. For ex.: [van Gogh,
   Self-Portrait](https://www.google.com/culturalinstitute/beta/asset/self-portrait/mwF3N6F_RfJ4_w).

All the collected data is stored in [MongoDb](https://docs.mongodb.com/manual/installation/).  
Images are stored on disk.

One entry in database for an artwork looks like (some artworks cane have more fields):


    {
       "image_id" : "oz_mural-millerntor-gallery_kAFxJz3YnrJ4rw",
       "artist_name_extra" : "OZ",
       "title" : "Mural MILLERNTOR GALLERY",
       "artwork_slug" : "mural-millerntor-gallery_kAFxJz3YnrJ4rw",
       "image_url" : "https://lh5.ggpht.com/OT7x4vhUw28Nb7mtvO8h017Pgn-S0B-x2Q9Dej9p8I0SdD-U46UrODnMsRZQJw",
       "page_url" : "https://www.google.com/culturalinstitute/beta/asset/mural-millerntor-gallery/kAFxJz3YnrJ4rw",
       "artist_slug" : "oz",
       "artist_id" : "t2194x6zy1b",
       "dimensions" : "spray paint on wall, ca. 6.0 x 3.0m",
       "location_created" : "St. Pauli, Hamburg, Germany",
       "title_original" : "Mural MILLERNTOR GALLERY",
       "date" : "2012-09"
    }


### Dependencies
- [MongoDb 3.4](https://docs.mongodb.com/manual/installation/)
- Python 2.7
  - [Scrapy 1.3.3](https://doc.scrapy.org/en/latest/intro/install.html)
  - Pymongo 3.4.0

### Setup
TODO:

### Usage
`:~$ scrapy crawl googleart`

