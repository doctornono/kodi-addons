import sys
import urllib
import json

import xbmc
import xbmcgui
import xbmcplugin 
import xbmcaddon
import xbmcvfs

from lib.myTMDB import myTMDB, tmdb2kodi, myListItems
from lib.myTrakt import myTrakt
from lib.myFanartTV import myFanartTV
from lib.myUptobox import myUptobox

from lib import PTN


# base_url = plugin://plugin.video.doctornono.trailer/
base_url = sys.argv[0]
# int represetant l'addon
addon_handle = int(sys.argv[1])
# tous les paramètres envoyés dans l'url
args = urllib.parse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)

my_addon = xbmcaddon.Addon('plugin.video.doctornono.trailer')

#xbmcplugin.setContent(addon_handle, 'movies')


TRAKT_ACTIVE        = my_addon.getSetting("trakt-active")
FANART_TV_ACTIVE    = my_addon.getSetting("fanart-active")
UPTOBOX_ACTIVE      = my_addon.getSetting("uptobox-active")



def getTMDBParameters():
    parametresTMDB = {
        "username" 		: my_addon.getSetting("tmdb-username"),
        "password" 		: my_addon.getSetting("tmdb-password"),
        "api_key"  		: my_addon.getSetting("tmdb-key"),
        "langue" 		: my_addon.getSetting("tmdb-langue"),
        "token"         : my_addon.getSetting("tmdb-token"),
        "session_id" 	: my_addon.getSetting("tmdb-session-id"),
        "user_id"       : my_addon.getSetting("tmdb-user-id"),
        "sql_path" 		: xbmcvfs.translatePath(my_addon.getAddonInfo('profile'))
    } 

    return parametresTMDB

def getTraktParameters():
    parametresTrakt = {
        "username" 		: my_addon.getSetting("trakt-username"),
        "api_key"  		: my_addon.getSetting("trakt-key"),
        "client_secret" : my_addon.getSetting("trakt-clientsecret"),
        "access_token" 	: my_addon.getSetting("trakt-access-token"),
        "refresh_token" : my_addon.getSetting("trakt-refresh-token"),
        "expire" 		: my_addon.getSetting("trakt-expire")
    } 

    return parametresTrakt

def getUserParameters():
    parametresUser = {
        'userMoviesFavorites'  : userMoviesFavorites,
        'userMoviesRated'      : userMoviesRated,
        'userMoviesWatchlist'  : userMoviesWatchlist,
        'imdbMoviesTop250'     : imdbMoviesTop250,

        'userTVShowFavorites'  : userTVShowFavorites,
        'userTVShowRated'      : userTVShowRated,
        'userTVShowWatchlist'  : userTVShowWatchlist,
        'imdbTVShowsTop250'    : imdbTVShowsTop250
    }

    return parametresUser

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def writeNotification(message):
    dialog = xbmcgui.Dialog()
    dialog.notification('myTMDB', message, xbmcgui.NOTIFICATION_INFO, 5000)



def viewSelect(rtmdb):

    listitems = []
    for movie in rtmdb['results']:
        if 'release_date' in movie:
            year = ' (' + movie['release_date'][0:4] + ')'
        else:
            year = ''                   
        listitem = xbmcgui.ListItem(movie['title'] + year)
        if movie['poster_path'] is not None:
            listitem.setArt({'thumb': 'https://image.tmdb.org/t/p/original' + movie['poster_path']})
        listitems.append(listitem)
    dialog = xbmcgui.Dialog()
    ret = dialog.select(file['file_name'], listitems, useDetails = True)
    return ret  




def listAddSortMethod(media):
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    #xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_DATEADDED)
    
    #xbmcplugin.SORT_METHOD_EPISODE


"""
//////////// MOVIE ////////////
"""
def addMovie(tmdbID, url = '', isfolder = True, idliste = None, movie = {}):
    if movie == {}:
        movie = mytmdb.getMovie(tmdbID)
    data = t2k.listItemSetInfoMovie(str(tmdbID), movie, imdbMoviesTop250, userMoviesRated)
    mylistItem.listItemAddMovie(tmdbID, data, movie, url, isfolder, idliste, getUserParameters())

"""
//////////// TV SHoW ////////////
"""
def addTVShow(tmdbID, url = '', isfolder = True, idliste = None, tvshow = {}):
    if tvshow == {}:
        tvshow = mytmdb.getTVShow(tmdbID)
    data = t2k.listItemSetInfoTVShow(tmdbID, tvshow, imdbTVShowsTop250, userTVShowRated)
    mylistItem.listItemAddTVShow(tmdbID, data, tvshow, url, isfolder, idliste, getUserParameters())


def addSeasons(tmdbID):
    data = mytmdb.getTVShow(tmdbID)
    tvshow = t2k.listItemSetInfoTVShow(tmdbID, data, imdbTVShowsTop250, userTVShowRated)
    mylistItem.listItemAddSeasons(tmdbID, data, tvshow)


def addSeason(tmdbID, season_number):
    season = mytmdb.getTVShowSeason(tmdbID, season_number, force = True)
    tvshow = mytmdb.getTVShow(tmdbID)
   
    for episode in season['episodes']:
        infos = t2k.listItemSetInfoEpisode(tmdbID, tvshow, season , episode, imdbTVShowsTop250, userTVShowRated)
        mylistItem.listItemAddSeason(tmdbID, episode, infos)






def migrerTMDBversTrakt(cat):
    
    if cat == 'vote':
        rated = json.loads(mytmdb.userGetAllMovies('rated'))
        ids = []
        for film in rated['data']:
            id = {
                "rating": film['userrating'],
                "ids": {
                    "tmdb": film['tmdb_id']
                }
            }
            ids.append(id)
        mytrakt.addRatings('movies', ids)
    elif cat == 'vue':
        rated = json.loads(mytmdb.userGetAllMovies('rated'))
        ids = []
        for film in rated['data']:
            id = {
                "ids": {
                    "tmdb": film['tmdb_id']
                }
            }
            ids.append(id)        
        mytrakt.addMediaToHistory('movies', ids)
    elif cat == 'favoris':
        favs = json.loads(mytmdb.userGetAllMovies('favorite', force=True))
        ids = []
        for film in favs['data']:
            id = {
                "ids": {
                    "tmdb": film['tmdb_id']
                }
            }
            ids.append(id)        
        mytrakt.addMediaToCollection('movies', ids)      


def migrerTraktversStream():
    col = mytrakt.getCollection('shows')
    xbmc.log('+++++++++++++++++++++++++++++++++++++++++++++++++'+str(col))
    ids=[]
    i=0
    for film in col:
        
        id = {
            "ids": {
                "tmdb": film['show']['ids']['tmdb']
            }
        }
        ids.append(id)   
        i = i + 1
        if i == 1000:
            break         
    #xbmc.log(str(ids))
    #xbmc.log('++++++++++++++++++++++++++++++++++++++++++++++++++'+str(mytrakt.addMediaToCollection('movies', 842675 )))
    mytrakt.addMediatoUserList('eventuellement', ids, 'shows')

#//////////////////////// debut  //////////////////////////////////////////
mytmdb = myTMDB.myTMDB(getTMDBParameters())

if mytmdb.checkDatabaseExistSQL() == False : mytmdb.createDatabaseSQL()

userMoviesFavorites  = json.loads(mytmdb.userGetAllMovies('favorite'))
userMoviesRated      = json.loads(mytmdb.userGetAllMovies('rated'))
userMoviesWatchlist  = json.loads(mytmdb.userGetAllMovies('watchlist'))
imdbMoviesTop250     = json.loads(mytmdb.getIMDBTop250('movie'))

userTVShowFavorites  = json.loads(mytmdb.userGetAllTVShows('favorite'))
userTVShowRated      = json.loads(mytmdb.userGetAllTVShows('rated'))
userTVShowWatchlist  = json.loads(mytmdb.userGetAllTVShows('watchlist'))
imdbTVShowsTop250    = json.loads(mytmdb.getIMDBTop250('tvshow'))


t2k = tmdb2kodi.tmdb2kodi()
mylistItem = myListItems.myListItems(base_url, my_addon, addon_handle)
mytrakt = myTrakt.myTrakt(getTraktParameters())
u2b = myUptobox.myUptobox(my_addon.getSetting("uptobox-key"))



# ---------------------------ACCUEIL -------------------------
if mode is None:
    #migrerTraktversStream()
    #migrerTMDBversTrakt('favoris')
    #addMovie(406759, isfolder = True)
    #addTVShow(1402, isfolder= True) 
    #mytrakt.addMediaToCollection('movies', 842675 )

    mylistItem.listItemAddFolder('Rechercher',     'search.png',   {'mode': 'searchengine', 'page' : '1', 'q' : ''})
    mylistItem.listItemAddFolder('myTMDB',         'tmdb.png',     {'mode': 'mytmdb-menu'})

    if my_addon.getSetting("trakt-active") == 'true':
        mylistItem.listItemAddFolder('myTrakt',    'trakttv.png',    {'mode': 'trakt-menu', 'trakt-user' : my_addon.getSetting("trakt-username")})
    
    if my_addon.getSetting("uptobox-active") == 'true':
        mylistItem.listItemAddFolder('myUptobox',  'uptobox.png',  {'mode': 'uptobox-menu'})


# ---------------------------RECHERCHER -------------------------
elif mode[0] in ['searchengine']:
    mylistItem.listItemAddFolder('Recherche Films',        'search.png', {'mode': 'search', 'page' : '1', 'q' : ' ', 'type':'movie'})
    mylistItem.listItemAddFolder('Recherche Séries',       'search.png', {'mode': 'search', 'page' : '1', 'q' : ' ', 'type':'tv'})
    mylistItem.listItemAddFolder('Recherche Acteurs',      'search.png', {'mode': 'search', 'page' : '1', 'q' : ' ', 'type':'person'})
    mylistItem.listItemAddFolder('Recherche Sagas',        'search.png', {'mode': 'search', 'page' : '1', 'q' : ' ', 'type':'collection'})
    mylistItem.listItemAddFolder('Recherche Studios',      'search.png', {'mode': 'search', 'page' : '1', 'q' : ' ', 'type':'company'})
    mylistItem.listItemAddFolder('Recherche Mots-clés',    'search.png', {'mode': 'search', 'page' : '1', 'q' : ' ', 'type':'keyword'})

elif mode[0] in ['search']:
    page    = args['page'][0]
    q       = args['q'][0]
    search  = args['type'][0]

    if q == ' ':
        dialog = xbmcgui.Dialog()
        q = dialog.input('Votre recherche', defaultt='', type=xbmcgui.INPUT_ALPHANUM)

    param = {
        'page'  : page,
        'type'  : search
    }
    items = mytmdb.getSearch(q, param=param)

    mylistItem.listItemAddSeparator('search', '%s résultats - page %s/%s' % (items['total_results'],  page, items['total_pages']))

    for item in items['results']:
        try:
            if search == 'movie'        :       addMovie(item['id'], isfolder = True)
            if search == 'tv'           :       addTVShow(item['id'], isfolder = True)
            if search == 'person'       :       mylistItem.listItemAddPerson(item)
            if search == 'collection'   :       mylistItem.listItemAddSaga(item)
            if search == 'company'      :       mylistItem.listItemAddStudio(item)
            if search == 'keyword'      :       mylistItem.listItemAddTag(item)
        except:
            pass

    if items['total_pages'] != int(page):
        mylistItem.listItemAddFolder('Plus', 'next.png', {'mode': 'search', 'page' : int(page) + 1, 'q' : q, 'type': search})

    if search == 'movie'    :   xbmcplugin.setContent(addon_handle, 'movies')
    if search == 'tv'       :   xbmcplugin.setContent(addon_handle, 'tvshows')


# --------------------------- TMDB -------------------------
elif mode[0] in ['mytmdb-menu']:
    #movies
    mylistItem.listItemAddFolder('Liste de suivi',     'watchlist.png',    {'mode': 'mytmdb-watchlist', 'page' : '1'})
    mylistItem.listItemAddFolder('Favoris',            'favorites.png',    {'mode': 'mytmdb-favorites', 'page' : '1'})        
    mylistItem.listItemAddFolder('Films notés',        'rated.png',        {'mode': 'mytmdb-ratedmovies', 'page' : '1'})
    #tv
    mylistItem.listItemAddFolder('Liste de suivi',     'watchlist.png',    {'mode': 'mytmdb-tvshowwatchlist', 'page' : '1'})
    mylistItem.listItemAddFolder('Favoris',            'favorites.png',    {'mode': 'mytmdb-tvshowfavorites', 'page' : '1'})        
    mylistItem.listItemAddFolder('Séries notées',      'rated.png',        {'mode': 'mytmdb-tvshowrated', 'page' : '1'})
    #gestion des listes personnelles de movieDB
    mylistItem.listItemAddFolder('Créer une liste',    'listadd.png',      {'mode': 'mytmdb-createlist'}, isfolder = False, isPlayable=False)
    userlists = mytmdb.userGetLists()
    for list in userlists['results']:
        mylistItem.listItemAddList(list)

    mylistItem.listItemAddFolder('Autres listes tmdb',  'tmdb.png',        {'mode': 'mytmdb-tmdblists'})


elif mode[0] in ['mytmdb-list']:
    tmdbID = args['tmdbid'][0]
    items = mytmdb.getList(tmdbID)
    for item in items['items']:
        if item['media_type'] == 'movie':
            addMovie(str(item['id']), isfolder = True, idliste = tmdbID)
        elif item['media_type'] == 'tv':
            addTVShow(str(item['id']), isfolder = True, idliste = tmdbID) 
    
    xbmcplugin.setContent(addon_handle, 'videos')


elif mode[0] in ['mytmdb-favorites', 'mytmdb-watchlist', 'mytmdb-ratedmovies']:
    if mode[0] == 'mytmdb-watchlist':
        results = userMoviesWatchlist
    elif mode[0] == 'mytmdb-ratedmovies':
        results = userMoviesRated
    elif mode[0] == 'mytmdb-favorites':
        results = userMoviesFavorites

    # identifier tous les tmdbid qui ne sont pas dans sql    
    rows = mytmdb.selectMultipleSQL("SELECT tmdbid FROM movies")
    ids = [row['tmdbid'] for row in rows]

    for list in results['data']:
        if list['tmdb_id'] not in ids:
            # ajouter dans sql les films manquants
            mytmdb.getMovie(str(list['tmdb_id']), force= True)
    
    s = ",".join([str(i['tmdb_id']) for i in results['data']])
    rows = mytmdb.selectMultipleSQL("SELECT * FROM movies WHERE tmdbid IN (%s)"  % (str(s)))
    for row in rows:
        addMovie(str(row['tmdbid']), isfolder = True, movie = json.loads(row['jsontmdb']))
    #listAddSortMethod('movie')

    xbmcplugin.setContent(addon_handle, 'movies')


elif mode[0] in ['mytmdb-tvshowfavorites', 'mytmdb-tvshowwatchlist', 'mytmdb-tvshowrated']:
    if mode[0] == 'mytmdb-tvshowwatchlist':
        results = userTVShowWatchlist
    elif mode[0] == 'mytmdb-tvshowrated':
        results = userTVShowRated
    elif mode[0] == 'mytmdb-tvshowfavorites':
        results = userTVShowFavorites

    # identifier tous les tmdbid qui ne sont pas dans sql 
    rows = mytmdb.selectMultipleSQL("SELECT tmdbid FROM tvshows")
    ids = [row['tmdbid'] for row in rows]

    for list in results['data']:
        if list['tmdb_id'] not in ids:
            # ajouter dans sql les series manquantes
            mytmdb.getTVShow(str(list['tmdb_id']), force = True)
          
    s = ",".join([str(i['tmdb_id']) for i in results['data']])
    rows = mytmdb.selectMultipleSQL("SELECT * FROM tvshows WHERE tmdbid IN (%s)"  % (str(s)))
    for row in rows:
        addTVShow(str(row['tmdbid']), isfolder = True, tvshow = json.loads(row['jsontmdb']))

    xbmcplugin.setContent(addon_handle, 'tvshows')


elif mode[0] == 'mytmdb-tmdblists':
    mylistItem.listItemAddFolder('Actuellement', 'now_playing.png', {'mode': 'mytmdb-nowplaying', 'page' : '1'})
    mylistItem.listItemAddFolder('Prochainement', 'upcoming.png',   {'mode': 'mytmdb-upcoming', 'page' : '1'})
    mylistItem.listItemAddFolder('Populaire', 'popular.png',        {'mode': 'mytmdb-popular', 'page' : '1'})
    mylistItem.listItemAddFolder('Top Rated', 'top_rated.png',      {'mode': 'mytmdb-toprated', 'page' : '1'})

    mylistItem.listItemAddFolder('Diffusée aujourd\'hui', 'now_playing.png',    {'mode': 'mytmdb-airingtoday', 'page' : '1'})
    mylistItem.listItemAddFolder('Diffusée actuellement', 'upcoming.png',       {'mode': 'mytmdb-ontheair', 'page' : '1'})
    mylistItem.listItemAddFolder('Populaire', 'popular.png',                    {'mode': 'mytmdb-tvshowpopular', 'page' : '1'})
    mylistItem.listItemAddFolder('Top Rated', 'top_rated.png',                  {'mode': 'mytmdb-tvshowtoprated', 'page' : '1'})    


elif mode[0] in ['mytmdb-upcoming', 'mytmdb-popular', 'mytmdb-toprated', 'mytmdb-nowplaying']:
    if mode[0] == 'mytmdb-upcoming'     : type = 'upcoming'
    if mode[0] == 'mytmdb-popular'      : type = 'popular'
    if mode[0] == 'mytmdb-toprated'     : type = 'top_rated'
    if mode[0] == 'mytmdb-nowplaying'   : type = 'now_playing'

    page = args['page'][0]
    myLists = mytmdb.getMovies(type, {'page' : page} )
    for movie in myLists['results']:
        addMovie(str(movie['id']), isfolder = True)

    mylistItem.listItemAddFolder('Next', 'next.png', {'mode': mode[0], 'page' : str(int(page) + 1)})
    xbmcplugin.setContent(addon_handle, 'movies')


elif mode[0] in ['mytmdb-ontheair', 'mytmdb-tvshowpopular', 'mytmdb-tvshowtoprated', 'mytmdb-airingtoday']:
    if mode[0] == 'mytmdb-ontheair'         : type = 'on_the_air'
    if mode[0] == 'mytmdb-tvshowpopular'    : type = 'popular'
    if mode[0] == 'mytmdb-tvshowtoprated'   : type = 'top_rated'
    if mode[0] == 'mytmdb-airingtoday'      : type = 'airing_today'

    page = args['page'][0]
    myLists = mytmdb.getTVShows(type, {'page' : page} )
    for movie in myLists['results']:
        addTVShow(str(movie['id']), isfolder = True)

    mylistItem.listItemAddFolder('Next', 'next.png', {'mode': mode[0], 'page' : str(int(page) + 1)})
    xbmcplugin.setContent(addon_handle, 'tvshows')   


# --------------------------- MEDIAS -------------------------
elif mode[0] == 'movie':
    tmdbID = args['tmdbID'][0]
    addMovie(tmdbID, isfolder = False)
    mylistItem.listItemAddFolder('Bande-annonces',     'trailer.png',       {'mode': 'trailer', 'tmdbid' : tmdbID, 'media' : 'movies'})    
    mylistItem.listItemAddFolder('Acteurs',            'cast.png',          {'mode': 'cast', 'tmdbid' : tmdbID, 'media' : 'movies'})
    mylistItem.listItemAddFolder('Similaires',         'search.png',        {'mode': 'similar', 'tmdbid' : tmdbID, 'media' : 'movies'})
    mylistItem.listItemAddFolder('Recommandations',    'recommended.png',   {'mode': 'recommendations', 'tmdbid' : tmdbID, 'media' : 'movies'})


elif mode[0] == 'tvshow':
    tmdbID = args['tmdbID'][0]
    addSeasons(tmdbID)
    mylistItem.listItemAddFolder('Bande-annonces',     'trailer.png',       {'mode': 'trailer', 'tmdbid' : tmdbID, 'media' : 'tvshows'})    
    mylistItem.listItemAddFolder('Acteurs',            'cast.png',          {'mode': 'cast', 'tmdbid' : tmdbID, 'media' : 'tvshows'})
    mylistItem.listItemAddFolder('Similaires',         'search.png',        {'mode': 'similar', 'tmdbid' : tmdbID, 'media' : 'tvshows'})
    mylistItem.listItemAddFolder('Recommandations',    'recommended.png',   {'mode': 'recommendations', 'tmdbid' : tmdbID, 'media' : 'tvshows'})


elif mode[0] == 'trailer':
    tmdbID = args['tmdbid'][0]
    media = args['media'][0]
    if media == 'movies':   item = mytmdb.openMovie(tmdbID)   
    if media == 'tvshows':  item = mytmdb.openTVShow(tmdbID) 

    trailers = item['videos']
    trailerslist = trailers['results']
    
    if my_addon.getSetting("tmdb-langue") != 'en-US':
        if media == 'movies':   dataUS = mytmdb.getTrailersUS(tmdbID, 'movie')
        if media == 'tvshows':  dataUS = mytmdb.getTrailersUS(tmdbID, 'tv')
        trailersUS = dataUS['videos']
        trailerslist = trailerslist + trailersUS['results']
  
    for trailer in trailerslist:
        mylistItem.listItemAddTrailer(item, trailer)


elif mode[0] == 'cast':
    tmdbID = args['tmdbid'][0]
    media = args['media'][0]
    if media == 'movies':   item = mytmdb.getMovie(tmdbID)
    if media == 'tvshows':  item = mytmdb.getTVShow(tmdbID)
    cast = item['credits']
    for director in cast['crew']:
        if director['job'] == 'Director':
            mylistItem.listItemAddCast(item, director)
    for actor in cast['cast']:
        mylistItem.listItemAddCast(item, actor)


elif mode[0] in ['similar','recommendations']:
    tmdbID = args['tmdbid'][0]
    media = args['media'][0]
    if media == 'movies':
        items = mytmdb.getMovies(mode[0], {'idtmdb': tmdbID})
        for item in items['results']:
            addMovie(str(item['id']), isfolder = True) 
    elif media == 'tvshows':
        items = mytmdb.getTVShows(mode[0].replace('tv', ''), {'idtmdb': tmdbID})
        for item in items['results']:
            addTVShow(str(item['id']), isfolder = True)         

    xbmcplugin.setContent(addon_handle, media)


elif mode[0] in ['saga']:
    tmdbID = args['tmdbid'][0]
    items = mytmdb.getSaga(tmdbID)
    for item in items['parts']:
        addMovie(str(item['id']), isfolder = True, idliste = tmdbID) 
    xbmcplugin.setContent(addon_handle, 'movies')        


# rajouter les tvshows dans les résultats
elif mode[0] in ['studio']:
    tmdbID = args['tmdbid'][0]
    items = mytmdb.getStudio(tmdbID)
    for item in items['results']:
        addMovie(str(item['id']), isfolder = True, idliste = tmdbID) 
    
    xbmcplugin.setContent(addon_handle, 'videos')


# rajouter les tvshows dans les résultats
elif mode[0] in ['tag']:
    tmdbID = args['tmdbid'][0]
    items = mytmdb.getTag(tmdbID)
    for item in items['results']:
         addMovie(str(item['id']), isfolder = True, idliste = tmdbID) 
    
    xbmcplugin.setContent(addon_handle, 'videos')


elif mode[0] == 'actor':
    tmdbID = args['tmdbid'][0]
    r = mytmdb.getPeople(tmdbID)
    for item in r['cast']:
        try:
            if item['media_type'] == 'tv'       :   addTVShow(str(item['id']), isfolder=True) 
            if item['media_type'] == 'movie'    :   addMovie(str(item['id']), isfolder=True)
        except:
            pass
    for item in r['crew']:
        try:
            if item['job'] == 'Director':
                if item['media_type'] == 'tv'       :   addTVShow(str(item['id']), isfolder=True) 
                if item['media_type'] == 'movie'    :   addMovie(str(item['id']), isfolder=True)
        except:
            pass
            
    xbmcplugin.setContent(addon_handle, 'videos')


elif mode[0] == 'episodes':
    tmdbID = args['tmdbID'][0]
    season_number = args['season_number'][0]
    addSeason(tmdbID, season_number)

    xbmcplugin.setContent(addon_handle, 'episodes')




# --------------------------- TRAKT -------------------------

elif mode[0] in ['trakt-menu']:
    user =  args['trakt-user'][0]
    mylistItem.listItemAddFolder('Films Watchlist',        'watchlist.png',    {'mode': 'trakt-watchlist', 'type' : 'movies', 'user' : user})
    mylistItem.listItemAddFolder('Films Collection',       'favorites.png',    {'mode': 'trakt-collection', 'type' : 'movies', 'user' : user})        
    mylistItem.listItemAddFolder('Films Historique',       'rated.png',        {'mode': 'trakt-history', 'type' : 'movies', 'user' : user})
    mylistItem.listItemAddFolder('Films notés',            'rated.png',        {'mode': 'trakt-ratings', 'type' : 'movies', 'user' : user})

    mylistItem.listItemAddFolder('Progress Watched',       'favorites.png',    {'mode': 'trakt-progress', 'type' : 'shows', 'user' : user}) # NE MARCHE PAS
    mylistItem.listItemAddFolder('Progress Collected',     'favorites.png',    {'mode': 'trakt-progress', 'type' : 'shows', 'user' : user}) # NE MARCHE PAS


    
    mylistItem.listItemAddFolder('Séries Watchlist',       'watchlist.png',    {'mode': 'trakt-watchlist', 'type' : 'shows', 'user' : user})
    mylistItem.listItemAddFolder('Séries Collection',      'favorites.png',    {'mode': 'trakt-collection', 'type' : 'shows', 'user' : user})
    mylistItem.listItemAddFolder('Historique Séries',      'favorites.png',    {'mode': 'trakt-history', 'type' : 'shows', 'user' : user}) # affiche les episodes en  fait
    mylistItem.listItemAddFolder('Séries notées',          'rated.png',        {'mode': 'trakt-ratings', 'type' : 'shows', 'user' : user})


    mylistItem.listItemAddFolder('Episodes Collection',    'favorites.png',    {'mode': 'trakt-collection', 'type' : 'episodes', 'user' : user})  # NE MARCHE PAS
    mylistItem.listItemAddFolder('Séries en cours',        'favorites.png',    {'mode': 'trakt-progress', 'type' : 'shows', 'user' : user}) # NE MARCHE PAS
    mylistItem.listItemAddFolder('Upcoming schedule',      'favorites.png',    {'mode': 'trakt-upcoming', 'type' : 'shows', 'user' : user}) # detailler les episodes

    mylistItem.listItemAddFolder('Historique Episodes',    'favorites.png',    {'mode': 'trakt-history', 'type' : 'episodes', 'user' : user}) # detailler les episodes

    mylistItem.listItemAddFolder('Saisons notées',         'rated.png',        {'mode': 'trakt-ratings', 'type' : 'seasons', 'user' : user})  # NE MARCHE PAS
    mylistItem.listItemAddFolder('Episodes notés',         'rated.png',        {'mode': 'trakt-ratings', 'type' : 'episodes', 'user' : user}) # NE MARCHE PAS

    mylistItem.listItemAddFolder('Créer une liste',        'listadd.png',      {'mode': 'trakt-createlist'}, isfolder = False, isPlayable=False)
    mylistItem.listItemAddFolder('Mes listes Trakt',       'trakt.png',        {'mode': 'trakt-user-lists', 'user' : user})
    mylistItem.listItemAddFolder('Mes listes aimées',      'trakt.png',        {'mode': 'trakt-liked-lists', 'user' : user})
    mylistItem.listItemAddFolder('Trakt Social',           'trakt.png',        {'mode': 'trakt-social', 'user' : user})
    mylistItem.listItemAddFolder('Autres listes Trakt',    'trakt.png',        {'mode': 'trakt-lists', 'user' : user})


elif mode[0] in ['trakt-user-lists']:
    userlists = mytrakt.getUserLists(args['user'][0])
    for list in userlists:
        mylistItem.listItemAddTraktList(list)

elif mode[0] in ['trakt-liked-lists']:
    userlists = mytrakt.getUserLikedLists(args['user'][0])
    for list in userlists:
        mylistItem.listItemAddTraktLikedList(list)    

elif mode[0] in ['trakt-lists']:
    mylistItem.listItemAddFolder('Films trending',             'watchlist.png',    {'mode': 'trakt-trending', 'type' : 'movies'})
    mylistItem.listItemAddFolder('Films populaires',           'popular.png',      {'mode': 'trakt-popular', 'type' : 'movies'})        
    mylistItem.listItemAddFolder('Films les plus regardés',    'now_playing.png',  {'mode': 'trakt-now-playing', 'type' : 'movies'})
    mylistItem.listItemAddFolder('Films les plus vus',         'rated.png',        {'mode': 'trakt-most-viewed', 'type' : 'movies'})
    mylistItem.listItemAddFolder('Films les plus recommandés', 'watchlist.png',    {'mode': 'trakt-most-recommended', 'type' : 'shows'})

elif mode[0] in ['trakt-social']:
    mylistItem.listItemAddFolder('Mes amis',               'trakt.png',        {'mode': 'trakt-user-friends'})
    mylistItem.listItemAddFolder('Mes following',          'trakt.png',        {'mode': 'trakt-user-following'})
    mylistItem.listItemAddFolder('Mes followers',          'trakt.png',        {'mode': 'trakt-user-followers'})

elif mode[0] in ['trakt-list']:
    traktID = args['traktid'][0]
    items = mytrakt.getList(traktID)
    for item in items:
        if item['type'] == 'movie':
            addMovie(str(item['movie']['ids']['tmdb']), isfolder = True)
        elif item['type'] == 'show':
            addTVShow(str(item['show']['ids']['tmdb']), isfolder = True) 

    listAddSortMethod('movie')



elif mode[0] in ['trakt-watchlist', 'trakt-collection', 'trakt-history', 'trakt-ratings', 'trakt-trending', 'trakt-popular', 'trakt-now-playing', 'trakt-most-viewed', 'trakt-most-recommended' ]:
    type = args['type'][0]
    
    if 'user' in args:
        usertrakt = args['user'][0]

        if usertrakt == my_addon.getSetting("trakt-username"):
            if mode[0] == 'trakt-watchlist' : items = mytrakt.getWatchlist(type)
            if mode[0] == 'trakt-collection' : items = mytrakt.getCollection(type)
            if mode[0] == 'trakt-history' : items = mytrakt.getHistory(type)
            if mode[0] == 'trakt-ratings' : items = mytrakt.getRatings(type)
        else:
            if mode[0] == 'trakt-watchlist' : items = mytrakt.getUserWatchlist(type, usertrakt)
            if mode[0] == 'trakt-collection' : items = mytrakt.getUserCollection(type, usertrakt)
            if mode[0] == 'trakt-history' : items = mytrakt.getUserHistory(type, usertrakt)
            if mode[0] == 'trakt-ratings' : items = mytrakt.getUserRatings(type, usertrakt)

    if mode[0] == 'trakt-trending' : items = mytrakt.getTrending(type)
    if mode[0] == 'trakt-popular' : items = mytrakt.getPopular(type)
    if mode[0] == 'trakt-now-playing' : items = mytrakt.getMostWatched(type)
    if mode[0] == 'trakt-most-viewed' : items = mytrakt.getMostPlayed(type)
    if mode[0] == 'trakt-most-recommended' : items = mytrakt.getMostRecommended(type)

    for item in items:
        #xbmc.log('------------------------------'+str(item))
        if 'type' in item:
            if item['type'] == 'movie':
                addMovie(str(item['movie']['ids']['tmdb']), isfolder = True)
            elif item['type'] == 'show':
                addTVShow(str(item['show']['ids']['tmdb']), isfolder = True)
            elif item['type'] == 'episode':
                addTVShow(str(item['show']['ids']['tmdb']), isfolder = True)                
        elif 'movie' in item:
            addMovie(str(item['movie']['ids']['tmdb']), isfolder = True)
        elif 'show' in item:
            addTVShow(str(item['show']['ids']['tmdb']), isfolder = True)
        elif 'episode' in item:
            addTVShow(str(item['show']['ids']['tmdb']), isfolder = True)
    if type == "movies" : xbmcplugin.setContent(addon_handle, 'movies')
    if type == "shows" : xbmcplugin.setContent(addon_handle, 'tvshows')  



elif mode[0] in ['trakt-user-friends']:
    friends = mytrakt.getUserFriends()
    for list in friends:
        mylistItem.listItemAddTraktFriend(list)


elif mode[0] in ['trakt-user-following']:
    friends = mytrakt.getUserFollowing()
    for list in friends:
        mylistItem.listItemAddTraktFriend(list)


elif mode[0] in ['trakt-user-followers']:
    friends = mytrakt.getUserFollowers()
    for list in friends:
        mylistItem.listItemAddTraktFriend(list)



elif mode[0] in ['trakt-upcoming']:
    upcoming = mytrakt.getCalendarMyShows()
    dateprecedente =  ''
    for item in upcoming:
        idshow  = item['show']['ids']['tmdb']
        idepisode  = item['episode']['ids']['tmdb']
        # deux types de listItem : une date et un episode
        datediffusion = item['first_aired'][0:10]
        if datediffusion != dateprecedente:


            xbmc.log('------------------------------------------' + datediffusion + '---------------------------------------------')
            mylistItem.listItemAddSeparator('date', str(datediffusion))
            # Ajouter la date
            
        xbmc.log(str(item) + str( type(datediffusion)))
        season = mytmdb.getTVShowSeason(idshow, item['episode']['season'], force = True)
        tvshow = mytmdb.getTVShow(idshow)
    
        
        for episode in season['episodes']:
            if item['episode']['number'] == episode['episode_number']:
                li = xbmcgui.ListItem(episode['name'])
                li.setProperty('isplayable','true')
                infos = t2k.listItemSetInfoEpisode(idshow, tvshow, season , episode, imdbTVShowsTop250, userTVShowRated)
                infos[0]['media_type'] = 'episode'
                li.setInfo('video', infos[0])
                li.setCast(infos[2])
                li.setArt(infos[1])
                url = build_url({'mode': 'playepisode', 'tmdbID' : idepisode}) 
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = False) 
            # Ajouter l'episode
            #listItemSetInfoEpisode(tmdbID, tvshow, season, episode)
        
        dateprecedente = datediffusion




    """
    *********************************************
    ACTIONS TMDB
    *********************************************
    """
#FONCTIONNEL
elif mode[0] == 'mytmdb-createlist':
    dialog = xbmcgui.Dialog()
    name = dialog.input('Nom de la liste', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
    if name != "":
        description = dialog.input('Description de la liste', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
        retour = mytmdb.createList(name, description)
    xbmc.executebuiltin('Container.Refresh')
    if retour['success'] == True:
        writeNotification('Nouvelle liste créée %s (%s)' % (name, str(retour['list_id'])))
    else:
        writeNotification('Erreur %s - %s' % (name, str(retour['status_message'])))

#FONCTIONNEL
elif mode[0] == 'mytmdb-deletelist':
    id = args['id'][0]
    retour = mytmdb.userDeleteList(id)
    xbmc.executebuiltin('Container.Refresh')
    writeNotification('La liste a été supprimée %s' % (id))

#FONCTIONNEL
elif mode[0] == 'mytmdb-addmovietolist':
    id = args['id'][0]
    myLists = mytmdb.userGetLists()
    ids     = [list['id'] for list in myLists['results']]
    labels  = [list['name'] for list in myLists['results']]

    dialog = xbmcgui.Dialog()
    liste = dialog.select('Choisissez une liste', labels, useDetails = True)
    if liste != -1:
        retour = mytmdb.addToList(id, ids[liste])
        if retour['success'] == True:
            writeNotification('Le film %s a été ajouté à la liste %s' % (id, labels[liste]))
        else:
            writeNotification('Erreur %s - %s' % (id, str(retour['status_message'])))

#FONCTIONNEL
elif mode[0] == 'mytmdb-addmovietonewlist':
    id = args['id'][0]
    dialog = xbmcgui.Dialog()
    name = dialog.input('Nom de la liste', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
    if name != "":
        description = dialog.input('Description de la liste', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
        r = mytmdb.createList(name, description)
        if r['success'] == True:
            retour = mytmdb.addToList(id, r['list_id'])
            if retour['success'] == True:
                writeNotification('Le film %s a été ajouté à la nouvelle liste %s' % (id, name))
            else:
                writeNotification('Erreur %s - %s' % (id, str(retour['status_message'])))        

#FONCTIONNEL
elif mode[0] == 'mytmdb-removefromlist':
    id = args['id'][0]
    idliste = args['idliste'][0]
    retour = mytmdb.userRemoveFromList(idliste, id)
    xbmc.executebuiltin('Container.Refresh')
    writeNotification('Le film %s a été retiré de la liste %s' % (id, idliste))  

#FONCTIONNEL
elif mode[0] == 'removefromwatchlist':
    tmdbid = args['id'][0]
    mytmdb.removeFromWatchlist(tmdbid)
    # supprimer de la key watchlist
    mytmdb.removeFromKey('tmdb_movies_watchlist', tmdbid)
    xbmc.executebuiltin('Container.Refresh')
    writeNotification('Film retiré de ma liste de suivi')

#FONCTIONNEL
elif mode[0] == 'removefromfavorites':
    tmdbid = args['id'][0]
    mytmdb.removeFromFavorites(tmdbid)
    # supprimer de la key favorites
    mytmdb.removeFromKey('tmdb_movies_favorites', tmdbid)
    xbmc.executebuiltin('Container.Refresh')    
    writeNotification('Film retiré de mes favoris')

#FONCTIONNEL
elif mode[0] == 'addtofavorites':
    tmdbid = args['id'][0]
    mytmdb.addToFavorites(tmdbid)
    # ajout à la key favorites
    mytmdb.addToKey('tmdb_movies_favorites', tmdbid)
    xbmc.executebuiltin('Container.Refresh')        
    writeNotification('Film ajouté à mes favoris')    

#FONCTIONNEL
elif mode[0] == 'addtowatchlist':
    tmdbid = args['id'][0]
    mytmdb.addToWatchlist(tmdbid)
    # ajout à la key watchlist
    mytmdb.addToKey('tmdb_movies_watchlist', tmdbid)
    xbmc.executebuiltin('Container.Refresh')   
    writeNotification('Film ajouté à ma liste de suivi')

#FONCTIONNEL
elif mode[0] == 'ratemovie':
    tmdbid = args['id'][0]
    dialog = xbmcgui.Dialog()    
    notes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    note = dialog.select('Choisissez une note', notes)
    if note != -1:
        mytmdb.rateMovie(tmdbid, notes[note])
        #Ajouter la note à la key tmdb_movies_rated
        mytmdb.updateRatingKey('tmdb_movies_rated', tmdbid, notes[note])
        xbmc.executebuiltin('Container.Refresh')
        writeNotification('Note ajoutée')   


    """
    *********************************************
    ACTIONS TRAKT
    *********************************************
    """

#FONCTIONNEL 
elif mode[0] == 'trakt-ratemovie':
    tmdbid = args['id'][0]
    dialog = xbmcgui.Dialog()    
    notes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    note = dialog.select('Choisissez une note', notes)
    if note != -1:
        mytrakt.addRating('movies', tmdbid, notes[note])
        #Ajouter la note à la key tmdb_movies_rated
        #mytmdb.updateRatingKey('tmdb_movies_rated', tmdbid, notes[note])
        #xbmc.executebuiltin('Container.Refresh')
        writeNotification('Note ajoutée') 

#FONCTIONNEL
elif mode[0] == 'trakt-addtowatchlist':
    tmdbid = args['id'][0]
    mytrakt.addMediaToWatchlist('movies', tmdbid)
    # ajout à la key watchlist
    #mytmdb.addToKey('tmdb_movies_watchlist', tmdbid)
    #xbmc.executebuiltin('Container.Refresh')   
    writeNotification('Film ajouté à ma liste de suivi')

    """
    /////////////////// TESTS DES CONNEXIONS  /////////////////////////////////
    """    
elif mode[0] ==  'test':
    test = args['test'][0]
    if test == 'tmdb':
        tm = myTMDB.myTMDB(getTMDBParameters())
        # tester api key
        writeNotification('Tester tmdb api key : %s' % tm.tester('api'))
        # tester identifiant

        
        #writeNotification(str(mytmdb.getMovies('popular')))

    elif test == 'trakt':
        tk = myTrakt.myTrakt(getTraktParameters())
        writeNotification(str(tk.reorderUserList(23392994, 'rank', 'desc')))
        # tester api key
        writeNotification('Tester Trakt api key : %s' % tk.tester('api'))
        # tester identifiant
        writeNotification('Tester Trakt identifiant : %s' % tk.tester('user'))
        # tester token
        writeNotification('Tester Trakt token : %s' % tk.tester('token'))

    elif test == 'trakt-install':
        tk = myTrakt.myTrakt(getTraktParameters())
        jDevice = tk.getDeviceCode()

        dialog = xbmcgui.Dialog()
        q = dialog.yesno('Trailer','Vous avez %s secondes pour aller sur l\'url %s et saisir le code suivant %s' % (jDevice['expires_in'], jDevice['verification_url'], jDevice['user_code']))
        if q == True:
            clientsecret = dialog.input('Votre Client secret : ', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
            jToken = tk.getToken(jDevice['device_code'], clientsecret)
            if jToken is int:
                writeNotification('Echec de la configuration : client secret faux')
            else:
                my_addon.setSettingString(id='trakt-access-token', value = jToken['access_token'])
                my_addon.setSettingString(id='trakt-refresh-token', value = jToken['refresh_token'])
                my_addon.setSettingString(id='trakt-clientsecret', value = clientsecret)
                my_addon.setSettingInt(id='trakt-expire', value=  jToken['created_at'] + jToken['expires_in'])

                writeNotification('Configuration Trakt : OK') 
        else:
            writeNotification('Abandon de la configuration') 
    

    elif test == 'fanarttv':
        # tester api key
        myfan = myFanartTV.myFanartTV(my_addon.getSetting("fanart-key"))
        if myfan.tester() is not None:     
            writeNotification('Tester Fanart.tv api key : OK')
        else:
            writeNotification('Tester Fanart.tv api key : Erreur')

    elif test == 'uptobox':
        # tester api key
        # tester les dossiers
        writeNotification(str(test))
        





# --------------------------- UPTOBOX -------------------------
elif mode[0] == 'uptobox-menu':
    mylistItem.listItemAddFolder('Films',          'movie.png',        {'mode': 'uptobox-movies'})    
    mylistItem.listItemAddFolder('Séries',         'tvshow.png',       {'mode': 'uptobox-tvshows'})
    mylistItem.listItemAddFolder('Importation',    'search.png',       {'mode': 'uptobox-importation'}, isfolder = False)
    mylistItem.listItemAddFolder('Maintenance',    'recommended.png',  {'mode': 'uptobox-maintenance'}, isfolder = False)

elif mode[0] == 'uptobox-maintenance':
    u2b.check()
    #ajouter les name dans sqlllite pourchaque fld_id
    """
    rows = mytmdb.getUptoboxFolderWithoutName()
    data = u2b.getFiles('', 'movie')
    data = data['data']
    folders = data['folders']
    for row in rows:
        for folder in folders:
            if row['fld_id'] == str(folder['fld_id']):
                mytmdb.updateUptoboxFolderName(row['fld_id'], row['tmdbid'], folder['name'])
    """


elif mode[0] == 'uptobox-importation':
    r = u2b.getFiles('', 'transfert')
    data = r['data']
    liste = data['files']

    for file in liste:    
        if file['file_descr'] == '':
                
            info = PTN.parse(file['file_name']) #'Hurlements.(Howling.I)).1981.MULTi.1080p.HDLight.x264.AC3-2.0-BLANK-Dread-Team.mkv')
            title = info['title']
            title = title.replace('.', ' ').replace(':', ' ').strip()
            title = str(title.encode('utf_8').decode('utf_8'))
            #xbmc.log('---------------------' + title)
            rtmdb = mytmdb.getSearch(title)

            if rtmdb['total_results'] == 1:
                year = ''
                if 'release_date' in rtmdb['results'][0]:  year = ' (' + rtmdb['results'][0]['release_date'][0:4] + ')'
                u2b.importMovie(file['file_code'], rtmdb['results'][0]['id'], rtmdb['results'][0]['title'] + year)

            if rtmdb['total_results'] > 1:
                ret = viewSelect(rtmdb)
                if ret > -1:
                    year = ''
                    if 'release_date' in rtmdb['results'][ret]:  year = ' (' + rtmdb['results'][ret]['release_date'][0:4] + ')'                    
                    u2b.importMovie(file['file_code'], rtmdb['results'][ret]['id'], rtmdb['results'][ret]['title'] + year)
                if ret == -1:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.input(str(file['file_name']),title ,xbmcgui.INPUT_ALPHANUM)
                    rtmdb = mytmdb.getSearch(ret)
                    #xbmc.log('****************' + ret + str(rtmdb))
                    ret = viewSelect(rtmdb)
                    if ret > -1:
                        year = ''
                        if 'release_date' in rtmdb['results'][ret]:  year = ' (' + rtmdb['results'][ret]['release_date'][0:4] + ')'                            
                        u2b.importMovie(file['file_code'], rtmdb['results'][ret]['id'], rtmdb['results'][ret]['title'] + year)

            if rtmdb['total_results'] == 0:
                dialog = xbmcgui.Dialog()
                ret = dialog.input(str(file['file_name']),title ,xbmcgui.INPUT_ALPHANUM)
                rtmdb = mytmdb.getSearch(ret)
                ret = viewSelect(rtmdb)
                if ret > -1:
                    year = ''
                    if 'release_date' in rtmdb['results'][ret]:  year = ' (' + rtmdb['results'][ret]['release_date'][0:4] + ')'    
                    u2b.importMovie(file['file_code'], rtmdb['results'][ret]['id'], rtmdb['results'][ret]['title'] + year)

        else:
            # importation si file_descr = tmdbid
            rtmdb = mytmdb.getMovie(file['file_descr'])
            year = ''
            if 'release_date' in rtmdb:  year = ' (' + rtmdb['release_date'][0:4] + ')'  
            #xbmc.log('++++++++++++++++++++++++++++++++++'+str(rtmdb['title'])               )
            u2b.importMovie(file['file_code'], file['file_descr'], str(rtmdb['title']) + year)



elif mode[0] == 'uptobox-movies':

    r = u2b.getFiles(media = 'movie')  
    folders = r['data']
    movies  = folders['folders']
    movies.sort(key=lambda x: x["name"])

    for movie in movies:
        tmdbid = mytmdb.getUptoboxFolder(movie['fld_id'])
        if tmdbid == False:
            #Trouver le tmdbid
            r = u2b.getFiles(str(movie['name']))
            rfiles = r['data']
            files = rfiles['files']
            for file in files:
                if file['file_descr'] != '':
                    tmdbid = file['file_descr']
            #Insérer le duo fld_id, tmdbid
            mytmdb.saveUptoboxFolder(str(movie['fld_id']), tmdbid, movie['name'])
            
        addMovie(tmdbid, isfolder = True)
        
    listAddSortMethod('movie')









elif mode[0] == 'play':
    tmdbID = args['tmdbID'][0]
    media = args['type'][0]
    name = mytmdb.getUptoboxFolderName(id)
    if name is not False:
        r = u2b.getFiles(name, media)
        data = r['data']
        files = data['files']
        for file in files:
            if movie == {}:
                movie = mytmdb.getMovie(tmdbID)
            #data = listItemSetInfoMovie(str(tmdbID))
            data = t2k.listItemSetInfoMovie(str(tmdbID), movie, imdbMoviesTop250, userMoviesRated)            
            myListItems.listItemAddFile(tmdbID, file, data)

    else:
        writeNotification('Envoyer lecture vers addon, tmdb id = ' + id)

xbmcplugin.endOfDirectory(addon_handle)