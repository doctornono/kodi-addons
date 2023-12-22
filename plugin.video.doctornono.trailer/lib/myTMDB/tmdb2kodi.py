from datetime import datetime, timedelta, date

class tmdb2kodi:
    def listItemSetInfoMovie(self, tmdbID, movie, imdbMoviesTop250, userMoviesRated):


        listGenres      = [item['name'] for item in movie['genres']]
        listCountries   = [item['name'] for item in movie['production_countries']]
        listStudios     = [item['name'] for item in movie['production_companies']]
        
        #///// Casting /////
        #listCast = [item['name'] for item in credits['cast']]
        credits = movie['credits']
        
        listCastAndRole = [{'name' : item['name'], 'role' : item['character'], 'thumbnail' : 'https://www.themoviedb.org/t/p/original' + str(item['profile_path']), 'order' :item['order']}  for item in credits['cast'] ]

        listDirector = []
        listWriter = []
        for item in credits['crew']:
            if item['job'] == 'Director':
                listDirector.append(item['name'])
            if item['job'] == 'Writer':
                listWriter.append(item['name'])

        keywords = movie['keywords']
        listTag = [item['name'] for item in keywords['keywords']]

        video = movie['videos']

        if movie['runtime'] is None: 
            runtime = 0
        else: 
            runtime = movie['runtime'] * 60

        # imdb top250
        imdb = imdbMoviesTop250
        top250 = 0
        for top in imdb['data']:
            if top['imdb_id'] == movie['imdb_id']:
                top250 = top['rank']

        # userrating et watched
        notes = userMoviesRated
        userrating = 0
        watched = 0
        for rating in notes['data']:
            if str(rating['tmdb_id']) == str(tmdbID):
                userrating = rating['userrating']
                watched  = 1


        # saga
        set = ''
        if 'belongs_to_collection"' in movie:
            set = movie['belongs_to_collection"'][0]['name']

        # trailer par defaut
        
        trailer = ''
        videos = movie['videos']['results']
        for video in videos:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                trailer = 'plugin://plugin.video.youtube/play/?video_id=' + video['key']

        
        # certifications
        certification = ''
        certifs = movie['release_dates']['results']
        for certif in certifs:
            if certif['iso_3166_1'] == 'FR':
                for item in certif['release_dates']:
                    if item['type'] == 3:
                        certification = certif['release_dates'][0]['certification']

        if certification != '' and certification !='U':
            certification = 'France:' + '-' + str(certification)




        infos = {    
                    
                    'mediatype'     :   'movie',                                                            # string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
                    'code'          :   tmdbID , #movie['id'],                                              # string (101) - Production code

                    'title'         :   movie['title'],
                    'originaltitle' :   movie['original_title'],
                    'sorttitle'     :   movie['title'],

                    'genre'         :   listGenres,                                                         # string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                    'year'          :   movie['release_date'],                                              # integer (2009)
                    'country'       :   listCountries,                                                      # string (Germany) or list of strings (["Germany", "Italy", "France"])
                    'duration'      :   runtime,                                                            # integer (245) - duration in seconds
                    'studio'        :   listStudios,                                                        # string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                    'premiered'     :   movie['release_date'],                                              # string (2005-03-04)

                    'director'      :   listDirector,                                                       # string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                    'writer'        :   listWriter,                                                         # string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                #  'castandrole'   :   listCastAndRole,                                                    # list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
                    'credits'       :   listWriter,                                                         # string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
                #  'cast'          :   listCast,                                                           # list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole   

                    'tagline'       :   movie['tagline'],                                                   # string (An awesome movie) - short description of movie
                    'plot'          :   movie['overview'],                                                  # string (Long Description)
                    'plotoutline'   :   movie['tagline'],                                                   # string (Short Description)
                    'tag'           :   listTag,                                                            # string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag

                    'imdbnumber'    :   movie['imdb_id'],                                                   #  string (tt0110293) - IMDb code

                    'rating'        :   movie['vote_average'],                                              # float (6.4) - range is 0..10
                    'votes'         :   movie['vote_count'],                                                # string (12345 votes)                
                    
                    'userrating'    :   userrating, #8.4,                                                   # integer (9) - range is 1..10 (0 to reset)
                    'top250'        :   top250,                                                             # integer (192)
            
                    'mpaa'          :   certification , #'PG-13',                                                            # string (PG-13)
                    'set'           :   set, #'Saga Batman',                                                      # string (Batman Collection) - name of the collection
                    'setoverview'   :   'All Batman movies',                                                # string (All Batman movies) - overview of the collection 
                    'showlink'      :   ["Battlestar Galactica", "Caprica"],                                # string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])      
                    'trailer'       :   trailer,                                                                 # string (/home/user/trailer.avi)

                    'playcount'     :   watched , #2,                                                                  # integer (2) - number of times this item has been played
                    'lastplayed'    :   '2009-04-05 23:16:04',                                              # string (Y-m-d h:m:s = 2009-04-05 23:16:04)

                    'path'          :   '' ,                                                                # string (/home/user/movie.avi)
                    'dateadded'     :   str(datetime.now())[0:19]                                           # string (Y-m-d h:m:s = 2009-04-05 23:16:04)
        }

        clearart = ''
        banner = ''
        clearlogo = ''
        thumb = ''
        fanart = ''
        if 'fanarttv' in movie:
            fanarttv = movie['fanarttv']
            if 'hdmovieclearart' in movie:
                clearart = fanarttv['hdmovieclearart']
                clearart = clearart[0]['url']
            if 'moviebanner' in movie:
                banner = fanarttv['moviebanner']
                banner = banner[0]['url']
            if 'hdmovielogo' in movie:
                clearlogo = fanarttv['hdmovielogo']
                clearlogo = clearlogo[0]['url']
            if 'moviethumb' in movie:
                thumb = fanarttv['moviethumb']
                thumb = thumb[0]['url']
            if 'moviefanart' in movie:
                fanart = fanarttv['moviefanart']
                fanart = thumb[0]['url']            

        if movie['poster_path'] == None :
            poster = ''
        else:
            poster = 'https://image.tmdb.org/t/p/w500' + movie['poster_path']

        if movie['backdrop_path'] != None :
            fanart = 'https://image.tmdb.org/t/p/original' + movie['backdrop_path']        

        art = {    
                    'thumb'     :  thumb,
                    'poster'    :  poster,
                    'fanart'    :  fanart,
                    'banner'    : banner, 
                    'clearart'  : clearart, 
                    'clearlogo' : clearlogo

                #    'landscape'  : 'https://images.fanart.tv/fanart/the-northman-62449fb348127.jpg',
                #    'icon'       : buildURLIcon('star.png')
        } 

        

        retour = []
        retour.append(infos)
        retour.append(art)
        retour.append(listCastAndRole)
        retour.append(video)
        return retour
    


    def listItemSetInfoTVShow(self, tmdbID, tvshow, imdbTVShowsTop250, userTVShowRated):

        listGenres = [item['name'] for item in tvshow['genres']]
        listCountries = [item['name'] for item in tvshow['production_countries']]
        listStudios = [item['name'] for item in tvshow['networks']]

        credits = tvshow['credits']
        listCast = [item['name'] for item in credits['cast']]
        listCastAndRole = [{'name' : item['name'], 'role' : item['character'], 'thumbnail' : 'https://www.themoviedb.org/t/p/original' + str(item['profile_path']), 'order' :item['order']}  for item in credits['cast'] ]

        listDirector = []
        listWriter = []
        for item in tvshow['created_by']:
            listDirector.append(item['name'])    

        keywords = tvshow['keywords']
        listTag = [item['name'] for item in keywords['results']]

        video = tvshow['videos']
        

       # if tvshow['episode_run_time'] is not []:
          #  runtime = tvshow['episode_run_time'][0]  * 60


        # imdb top250
        imdb = imdbTVShowsTop250
        top250 = 0
        for top in imdb['data']:
            if top['imdb_id'] == tvshow['external_ids']['imdb_id']:
                top250 = top['rank']
        
        # userrating et watched
        notes = userTVShowRated
        userrating = 0
        watched = 0
        for rating in notes['data']:
            if str(rating['tmdb_id']) == str(tmdbID):
                userrating = rating['userrating']
                watched  = 1

        # certification
        certification = ''
        certifications = tvshow['content_ratings']['results']
        for certif in certifications:
            if certif['iso_3166_1'] == 'FR':
                certification = certif['rating']
        
        if certification != '' and certification != 'U':
            certification = 'France:' + '-' + certification
        """
    genre	string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
    country	string (Germany) or list of strings (["Germany", "Italy", "France"])
    year	integer (2009)
    episode	integer (4)
    season	integer (1)
    sortepisode	integer (4)
    sortseason	integer (1)
    episodeguide	string (Episode guide)
    showlink	string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])
    top250	integer (192)
    setid	integer (14)
    tracknumber	integer (3)
    rating	float (6.4) - range is 0..10
    userrating	integer (9) - range is 1..10 (0 to reset)
    watched	deprecated - use playcount instead
    playcount	integer (2) - number of times this item has been played
    overlay	integer (2) - range is 0..7. See Overlay icon types for values
    cast	list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole
    castandrole	list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
    director	string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
    mpaa	string (PG-13)
    plot	string (Long Description)
    plotoutline	string (Short Description)
    title	string (Big Fan)
    originaltitle	string (Big Fan)
    sorttitle	string (Big Fan)
    duration	integer (245) - duration in seconds
    studio	string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
    tagline	string (An awesome movie) - short description of movie
    writer	string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
    tvshowtitle	string (Heroes)
    premiered	string (2005-03-04)
    status	string (Continuing) - status of a TVshow
    set	string (Batman Collection) - name of the collection
    setoverview	string (All Batman movies) - overview of the collection
    tag	string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
    imdbnumber	string (tt0110293) - IMDb code
    code	string (101) - Production code
    aired	string (2008-12-07)
    credits	string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
    lastplayed	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
    album	string (The Joshua Tree)
    artist	list (['U2'])
    votes	string (12345 votes)
    path	string (/home/user/movie.avi)
    trailer	string (/home/user/trailer.avi)
    dateadded	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
    mediatype	string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
    dbid	integer (23) - Only add this for items which are part of the local db. You also need to set the correct 'mediatype'!

        """


        infos = {    
                    
                    'mediatype'     :   'tvshow',                                                            # string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
                    'code'          :   tmdbID , #movie['id'],                                              # string (101) - Production code

                    'title'         :   tvshow['name'],
                    'originaltitle' :   tvshow['original_name'],
                    'sorttitle'     :   tvshow['name'],
                    'tvshowtitle'   :   tvshow['name'],

                    'status'        :   tvshow['status'],
                    'saison'        :   int(tvshow['number_of_seasons']),
                    'episode'       :   int(tvshow['number_of_episodes']),

                    'genre'         :   listGenres,                                                         # string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                    'year'          :   tvshow['first_air_date'],                                              # integer (2009)
                    'country'       :   listCountries,                                                      # string (Germany) or list of strings (["Germany", "Italy", "France"])
                  #  'duration'      :   runtime,                                  # integer (245) - duration in seconds
                    'studio'        :   listStudios,                                                        # string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                    'premiered'     :   tvshow['first_air_date'],                                              # string (2005-03-04)

                    'director'      :   listDirector,                                                       # string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                    'writer'        :   listWriter,                                                         # string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                #  'castandrole'   :   listCastAndRole,                                                    # list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
                    'credits'       :   listWriter,                                                         # string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
                #  'cast'          :   listCast,                                                           # list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole   

                    'tagline'       :   tvshow['tagline'],                                                   # string (An awesome movie) - short description of movie
                    'plot'          :   tvshow['overview'],                                                  # string (Long Description)
                    'plotoutline'   :   tvshow['tagline'],                                                   # string (Short Description)
                    'tag'           :   listTag,                                                            # string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
                    

                    'imdbnumber'    :   tvshow['external_ids']['imdb_id'],                                   #  string (tt0110293) - IMDb code

                    'rating'        :   tvshow['vote_average'],                                              # float (6.4) - range is 0..10
                    'votes'         :   tvshow['vote_count'],                                                # string (12345 votes)                
                    
                    'userrating'    :   userrating, #8.4,                                                   # integer (9) - range is 1..10 (0 to reset)
                    'top250'        :   top250,                                                             # integer (192)
            
                    'mpaa'          :   certification, #'PG-13',                                                            # string (PG-13)
                # 'set'           :   set, #'Saga Batman',                                                      # string (Batman Collection) - name of the collection
                # 'setoverview'   :   'All Batman movies',                                                # string (All Batman movies) - overview of the collection 
                # 'showlink'      :   ["Battlestar Galactica", "Caprica"],                                # string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])      
                    'trailer'       :   '',                                                                 # string (/home/user/trailer.avi)

                    'playcount'     :   watched , #2,                                                                  # integer (2) - number of times this item has been played
                    'lastplayed'    :   '2009-04-05 23:16:04',                                              # string (Y-m-d h:m:s = 2009-04-05 23:16:04)

                    'path'          :   ''                                                                  # string (/home/user/movie.avi)
        }

        clearart = ''
        banner = ''
        clearlogo = ''
        thumb = ''
        if 'fanarttv' in tvshow:
            fanart = tvshow['fanarttv']
            if 'hdclearart' in fanart:
                clearart = fanart['hdclearart']
                clearart = clearart[0]['url']
            if 'tvbanner' in fanart:
                banner = fanart['tvbanner']
                banner = banner[0]['url']
            if 'hdtvlogo' in fanart:
                clearlogo = fanart['hdtvlogo']
                clearlogo = clearlogo[0]['url']
            if 'tvthumb' in fanart:
                thumb = fanart['tvthumb']
                thumb = thumb[0]['url']

        if tvshow['poster_path'] == None :
            #thumb = ''
            poster = ''
        else:
            #thumb = 'https://image.tmdb.org/t/p/w185' + movie['poster_path']
            poster = 'https://image.tmdb.org/t/p/w500' + tvshow['poster_path']

        art = {    
                    'thumb'     :  thumb, #'https://image.tmdb.org/t/p/w185' + poster_path, 
                    'poster'    :  poster, #'https://image.tmdb.org/t/p/w500' + poster_path,
                    'fanart'    :  'https://image.tmdb.org/t/p/original' + tvshow['backdrop_path'] if tvshow['backdrop_path'] != None else '', #'https://image.tmdb.org/t/p/original' + poster_path,

                    'banner'    : banner, #'https://images.fanart.tv/fanart/the-northman-625329abe0120.jpg',
                    'clearart'  : clearart, #'https://images.fanart.tv/fanart/the-northman-62444bfab1c9c.png',
                    'clearlogo' : clearlogo #'https://images.fanart.tv/fanart/the-northman-61ec51afd4b0c.png',
                # 'landscape' : 'https://images.fanart.tv/fanart/the-northman-62449fb348127.jpg',
                #  'icon'      : buildURLIcon('star.png') #'https://library.kissclipart.com/20180831/rfw/kissclipart-film-vector-png-clipart-hollywood-clip-art-aa8d3c1c62df7f9e.pngs'
        } 

        

        retour = []
        retour.append(infos)
        retour.append(art)
        retour.append(listCastAndRole)
        retour.append(video)

        #xbmc.log(str(retour))
        return retour







    def listItemSetInfoEpisode(self, tmdbID, tvshow, season, episode, imdbTVShowsTop250, userTVShowRated):

        listGenres = [item['name'] for item in tvshow['genres']]
        listCountries = [item['name'] for item in tvshow['production_countries']]
        listStudios = [item['name'] for item in tvshow['networks']]

        credits = tvshow['credits']
        listCast = [item['name'] for item in credits['cast']]
        listCastAndRole = [{'name' : item['name'], 'role' : item['character'], 'thumbnail' : 'https://www.themoviedb.org/t/p/original' + str(item['profile_path']), 'order' :item['order']}  for item in episode['guest_stars'] ]

        listDirector = []
        listWriter = []
        for item in episode['crew']:
            if item['job'] == 'Director':
                listDirector.append(item['name'])    
            if item['job'] == 'Writer':
                listWriter.append(item['name']) 


        keywords = tvshow['keywords']
        listTag = [item['name'] for item in keywords['results']]

        video = tvshow['videos']
        
        runtime = 0
        """
        if tvshow['episode_run_time'] is []: 
            runtime = 0
        else: 
            runtime = tvshow['episode_run_time'][0] * 60
        """
        # imdb top250
        imdb = imdbTVShowsTop250
        top250 = 0
        for top in imdb['data']:
            if top['imdb_id'] == tvshow['external_ids']['imdb_id']:
                top250 = top['rank']
        
        # userrating et watched
        notes = userTVShowRated
        userrating = 0
        watched = 0
        for rating in notes['data']:
            if str(rating['tmdb_id']) == str(tmdbID):
                userrating = rating['userrating']
                watched  = 1

        infos = {    
                    
                    'mediatype'     :   'episode',                                                            # string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
                    'code'          :   episode['id'],                                              # string (101) - Production code

                    'title'         :   episode['name'],
                    #'originaltitle' :   tvshow['original_name'],
                    'sorttitle'     :   episode['name'],
                    'tvshowtitle'   :   tvshow['name'],

                #  'status'        :   tvshow['status'],
                    'saison'        :   episode['season_number'],
                    'episode'       :   episode['episode_number'],
                    'sortepisode'   :	3, #integer (4)
                    'sortseason'    :	5, #integer (1)

                    'genre'         :   listGenres,                                                         # string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
                    'year'          :   episode['air_date'],                                              # integer (2009)
                    'country'       :   listCountries,                                                      # string (Germany) or list of strings (["Germany", "Italy", "France"])
                    #'duration'      :   episode['runtime'] * 60,                                            # integer (245) - duration in seconds
                    'studio'        :   listStudios,                                                        # string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
                    'premiered'     :   episode['air_date'],                                              # string (2005-03-04)

                    'director'      :   listDirector,                                                       # string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
                    'writer'        :   listWriter,                                                         # string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
                #  'castandrole'   :   listCastAndRole,                                                    # list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
                    'credits'       :   listWriter,                                                         # string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
                #  'cast'          :   listCast,                                                           # list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole   

                    #'tagline'       :   tvshow['tagline'],                                                   # string (An awesome movie) - short description of movie
                    'plot'          :   episode['overview'],                                                  # string (Long Description)
                    #'plotoutline'   :   tvshow['tagline'],                                                   # string (Short Description)
                    'tag'           :   listTag,                                                            # string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
                    

                    'imdbnumber'    :   tvshow['external_ids']['imdb_id'],                                   #  string (tt0110293) - IMDb code

                    'rating'        :   episode['vote_average'],                                              # float (6.4) - range is 0..10
                    'votes'         :   episode['vote_count'],                                                # string (12345 votes)                
                    
                    'userrating'    :   userrating, #8.4,                                                   # integer (9) - range is 1..10 (0 to reset)
                    'top250'        :   top250,                                                             # integer (192)
            
                    'mpaa'          :   'PG-13',                                                            # string (PG-13)
                # 'set'           :   set, #'Saga Batman',                                                      # string (Batman Collection) - name of the collection
                # 'setoverview'   :   'All Batman movies',                                                # string (All Batman movies) - overview of the collection 
                # 'showlink'      :   ["Battlestar Galactica", "Caprica"],                                # string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])      
                    'trailer'       :   '',                                                                 # string (/home/user/trailer.avi)

                    'playcount'     :   watched , #2,                                                                  # integer (2) - number of times this item has been played
                    'lastplayed'    :   '2009-04-05 23:16:04',                                              # string (Y-m-d h:m:s = 2009-04-05 23:16:04)

                    'path'          :   ''                                                                  # string (/home/user/movie.avi)
        }

        clearart = ''
        banner = ''
        clearlogo = ''
        thumb = ''
        if 'fanarttv' in tvshow:
            fanart = tvshow['fanarttv']
            if 'hdclearart' in fanart:
                clearart = fanart['hdclearart']
                clearart = clearart[0]['url']
            if 'tvbanner' in fanart:
                banner = fanart['tvbanner']
                banner = banner[0]['url']
            if 'hdtvlogo' in fanart:
                clearlogo = fanart['hdtvlogo']
                clearlogo = clearlogo[0]['url']
            if 'tvthumb' in fanart:
                thumb = fanart['tvthumb']
                thumb = thumb[0]['url']

        if episode['still_path'] == None :
            #thumb = ''
            fanart = ''
        else:
            #thumb = 'https://image.tmdb.org/t/p/w185' + movie['poster_path']
            fanart = 'https://image.tmdb.org/t/p/w500' + episode['still_path']

        art = {    
                    'thumb'     :  thumb, #'https://image.tmdb.org/t/p/w185' + poster_path, 
                # 'poster'    :  poster, #'https://image.tmdb.org/t/p/w500' + poster_path,
                    'fanart'    :  fanart , #'https://image.tmdb.org/t/p/original' + tvshow['backdrop_path'] if tvshow['backdrop_path'] != None else '', #'https://image.tmdb.org/t/p/original' + poster_path,

                    'banner'    : banner, #'https://images.fanart.tv/fanart/the-northman-625329abe0120.jpg',
                    'clearart'  : clearart, #'https://images.fanart.tv/fanart/the-northman-62444bfab1c9c.png',
                    'clearlogo' : clearlogo #'https://images.fanart.tv/fanart/the-northman-61ec51afd4b0c.png',
                # 'landscape' : 'https://images.fanart.tv/fanart/the-northman-62449fb348127.jpg',
                #  'icon'      : buildURLIcon('star.png') #'https://library.kissclipart.com/20180831/rfw/kissclipart-film-vector-png-clipart-hollywood-clip-art-aa8d3c1c62df7f9e.pngs'
        } 

        

        retour = []
        retour.append(infos)
        retour.append(art)
        retour.append(listCastAndRole)
        retour.append(video)

        #xbmc.log(str(retour))
        return retour




