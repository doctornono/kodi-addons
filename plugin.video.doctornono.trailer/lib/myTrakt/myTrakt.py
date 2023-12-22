from urllib import request
from urllib import error

import json

class myTrakt:
	def __init__(self, parametres):
		# Constantes
		self.TRAKT_API_VERSION 	= '2'								
		self.TRAKT_URLAPI 		= 'https://api.trakt.tv'

		self.setParameters(parametres)


	def setParameters(self, parametres):
		# Variables User
		self.TRAKT_KEY 			= parametres["api_key"]		
		self.TRAKT_USERNAME 	= parametres["username"] 	
		# Variables Authentification
		self.TRAKT_SECRET 		= parametres["client_secret"] 
		self.TRAKT_BEARER 		= parametres["access_token"]
		self.TRAKT_REFRESH_TOKEN= parametres["refresh_token"]
		self.TRAKT_EXPIRE		= parametres["expire"]		


	def getParameters(self):
		parametres = {
			"username" 		: self.TRAKT_USERNAME,
			"api_key"  		: self.TRAKT_KEY,
			"client_secret" : self.TRAKT_SECRET,
			"access_token" 	: self.TRAKT_BEARER,
			"refresh_token" : self.TRAKT_REFRESH_TOKEN,
			"expire" 		: self.TRAKT_EXPIRE
		}

		return parametres


	def getHeaders(self):
		headers = {
			'Content-Type'		: 'application/json',
			'trakt-api-version'	: self.TRAKT_API_VERSION,
			'trakt-api-key'		: self.TRAKT_KEY
		}		

		return headers

	
	# Appelle l'API  et retourne le JSON
	# method : GET, POST, PUT
	# OAuth = True pour utiliser l'access token
	def getJSON(self, url, method = "GET", data = False, OAuth = False, headers = False):
		if headers is False:
			headers = self.getHeaders()

		req = request.Request('%s/%s' % (self.TRAKT_URLAPI, url), method = method, headers = headers)
		if OAuth is True:
			req.add_header('Authorization', 'Bearer ' + self.TRAKT_BEARER)
		
		if data is not False:
			data = json.dumps(data).encode()

			try:
				r = request.urlopen(req, data = data)
			except error.HTTPError as e:
				return e.code

		else:
			try:
				r = request.urlopen(req)
			except error.HTTPError as e:
				return e.code			

		content = r.read()
		r.close()
		return json.loads(content)		


	##########################################
	# CALENDAR
	##########################################

	# Equivalent de Upcoming schedule
	def getCalendarMyShows(self):
		return self.getJSON('calendars/my/shows', OAuth=True)

	def getCalendarMyNewShows(self):
		return self.getJSON('calendars/my/shows/new', OAuth=True)

	def getCalendarMySeasonPremieres(self):
		return self.getJSON('calendars/my/shows/premieres', OAuth=True)

	def getCalendarMyMovies(self):
		return self.getJSON('calendars/my/movies', OAuth=True)

	def getCalendarMyDVD(self):
		return self.getJSON('calendars/my/dvd', OAuth=True)

	def getCalendarAllShows(self):
		return self.getJSON('calendars/all/shows', OAuth=True)

	def getCalendarAllNewShows(self):
		return self.getJSON('calendars/all/shows/new', OAuth=True)

	def getCalendarAllSeasonPremieres(self):
		return self.getJSON('calendars/all/shows/premieres', OAuth=True)			

	def getCalendarAllMovies(self):
		return self.getJSON('calendars/all/movies', OAuth=True)

	def getCalendarAllDVD(self):
		return self.getJSON('calendars/all/dvd', OAuth=True)

	# CERTIFICATIONS
	def getCertificationsList(self, media = 'movies'):
		return self.getJSON('certifications/%s' % media)

	# COUNTRIES
	def getCountriesList(self, media = 'movies'):
		return self.getJSON('countries/%s' % media)

	# GENRES
	def getGenresList(self, media = 'movies'):
		return self.getJSON('genres/%s' % media)

	# LANGUAGES
	def getLanguagesList(self, media = 'movies'):
		return self.getJSON('languages/%s' % media)
	
	# NETWORKS
	def getNetworksList(self):
		return self.getJSON('networks')




	# LISTES TRAKT CLASSIQUES
	def getTrending(self, media = 'movies'):
		return self.getJSON('%s/trending' % media)

	def getPopular(self, media = 'movies'):
		return self.getJSON('%s/popular' % media)

	def getMostWatched(self, media = 'movies'):
		return self.getJSON('%s/watched/weekly' % media)

	def getMostPlayed(self, media = 'movies'):
		return self.getJSON('%s/played/weekly' % media)

	def getMostRecommended(self, media = 'movies'):
		return self.getJSON('%s/recommended/weekly' % media)



	# Lists/List Items/Get items on a list
	def getList(self, idliste):
		return self.getJSON('lists/%s/items/' % idliste)


	# LISTES UTILISATEUR
	def getUserStats(self, user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/settings', OAuth= True)	

	# Users/Lists/Get a user's personal lists
	def getUserLists(self, user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/lists' % user)

	# Users/List Items/Get items on a personal list
	def getUserListItems(self, listeid,  type = 'all', user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/lists/%s/items/%s' % (user, listeid, type))

	# Users/Watchlist/Get watchlist
	def getUserWatchlist(self, user, type = 'all'):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/watchlist/%s' % (user, type))

	# Users/History/Get watched history
	def getUserHistory(self, type = 'all', user = ''):
		if user == '': user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/history/%s' % (user, type))

	# Users/Collection/Get collection
	def getUserCollection(self, type = 'all', user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/collection/%s' % (user, type))

	# Users/Ratings/Get ratings
	def getUserRatings(self, type = 'all', user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/ratings/%s' % (user, type))
	
	# Users/Watched/Get watched
	def getUserWatched(self, type = 'all', user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/watched/%s' % (user, type))	

	# Retourne les listes aimées par l'utilisateur
	def getUserLikedLists(self, user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/likes/lists' % user, OAuth= True)		

	# Retourne les amis de l'utilisateur
	def getUserFriends(self, user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/friends' % user, OAuth= True)				

	# Retourne les following de l'utilisateur
	def getUserFollowing(self, user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/following' % user, OAuth= True)

	# Retourne les followers de l'utilisateur
	def getUserFollowers(self, user = None):
		if user == None: user = self.TRAKT_USERNAME
		return self.getJSON('users/%s/followers' % user, OAuth= True)					


	# Shows/Watched Progress/Get show watched progress
	def getWatchedProgress(self, tmdbid):
		return self.getJSON('shows/%s/progress/watched' % tmdbid, OAuth= True)



	def getSync(self, action, media):
		return self.getJSON('sync/%s/%s' % (action, media), OAuth= True)	

	def getCollection(self,  media):
		return self.getSync('collection', media)

	def getHistory(self,  media):
		return self.getSync('history', media)

	def getWatched(self,  media):
		return self.getSync('watched', media)

	# media = movies, shows, seasons, episodes
	def getWatchlist(self,  media):
		return self.getSync('watchlist', media)

	def getRatings(self,  media):
		return self.getSync('ratings', media)						

	# Retourne les activités de l'utilisateur
	# Permet de savoir si la watchlist a  été modifiée par ex
	# Voir pour utiliser ces infos pour le cache sql
	def getLastActivities(self,  media):
		return self.getSync('last_activities', media)



	# ACTIONS
	def setSync(self, media, tmdbid, action):
		if isinstance(tmdbid, int):
			data =   {
				media: [{
				"ids": {
					"tmdb": tmdbid
				}
				}]
			}		
		else:
			data = {
				media: tmdbid
			}
		return self.getJSON('sync/%s' % action, data= data, OAuth= True, method="POST")	

	# Permet d'ajouter un media à sa collection
	# media = 'movies', shows, seasons, episodes
	def addMediaToCollection(self, media, tmdbid):
		return self.setSync(media, tmdbid, 'collection')	

	# Permet de retirer un media de sa collection
	# media = 'movies', shows, seasons, episodes
	def removeMediaFromCollection(self, media, tmdbid):
		return self.setSync(media, tmdbid, 'collection/remove')

	# Permet d'ajouter un media à sa history
	# media = 'movies', shows, seasons, episodes
	def addMediaToHistory(self, media, tmdbid):
		return self.setSync(media, tmdbid, 'history')	

	# Permet de retirer un media de sa history
	# media = 'movies', shows, seasons, episodes
	def removeMediaFromHistory(self, media, tmdbid):
		return self.setSync(media, tmdbid, 'history/remove')

	# Permet d'ajouter un media à sa watchlist
	# media = 'movies', shows, seasons, episodes
	def addMediaToWatchlist(self, media, tmdbid):
		return self.setSync(media, tmdbid, 'watchlist')	

	# Permet de retirer un media de sa watchlist
	# media = 'movies', shows, seasons, episodes
	def removeMediaFromWatchlist(self, media, tmdbid):
		return self.setSync(media, tmdbid, 'watchlist/remove')

	# Permet de noter un media 
	# media = 'movies', shows, seasons, episodes
	def addRating(self, media, tmdbid, rating):
		data =   {
			media: [{
				"rating" : rating,
				"ids": {
					"tmdb": tmdbid
				}
			}]
		}

		return self.getJSON('sync/ratings', data= data, OAuth= True, method="POST")	


	# Permet de noter plusieurs medias
	# media = 'movies', shows, seasons, episodes
	def addRatings(self, media, ratings):
		data =   {
			media: ratings
		}

		return self.getJSON('sync/ratings', data= data, OAuth= True, method="POST")	



	# Permet d'ajouter un media à une liste utilisateur
	# media = 'movies', shows, seasons, episodes, people
	# nomliste : Id ou slug name de la liste user Trakt = 'la-derniere-seance-guerre' ou 23392994
	def addMediatoUserList(self, nomliste, tmdbid, media):
		if isinstance(tmdbid, int):
			data =   {
				media: [{
				"ids": {
					"tmdb": tmdbid
				}
				}]
			}		
		else:
			data = {
				media: tmdbid
			}		
		return self.getJSON('users/%s/lists/%s/items' % (self.TRAKT_USERNAME, nomliste), data= data, OAuth= True, method="POST")		

	# Permet d'oter un media à une liste utilisateur
	# media = 'movies', shows, seasons, episodes, people
	# nomliste : Id ou slug name de la liste user Trakt = 'la-derniere-seance-guerre' ou 23392994
	def removeMediatoUserList(self, nomliste, tmdbid, media):
		data =   {
			media: [{
			"ids": {
				"tmdb": tmdbid
			}
			}]
		}

		return self.getJSON('users/%s/lists/%s/items/remove' % (self.TRAKT_USERNAME, nomliste), data= data, OAuth= True, method="POST")		

	# Permet de réordonner une liste personelle
	# sort_by : rank, added, title, released, runtime, popularity, percentage, votes, my_rating, random, watched, collected
	# sort_how : asc ou desc
	def reorderUserList(self, nomliste, sort_by, sort_how):
		data =   {
			"sort_by": sort_by,
			"sort_how" : sort_how
		}

		return self.getJSON('users/%s/lists/%s' % (self.TRAKT_USERNAME, nomliste), data= data, OAuth= True, method="PUT")	



	# Permet de scrobbler sur Trakt
	# Scrobble/Start
	# action = 'stop' et progress = 100 marque le media comme Vu
	# action	:	start, pause, stop
	# media		:	movie, episode
	def scrobble(self, action, media, tmdbid, progress = 100):
		data =   {
			media: {
			"ids": {
				"tmdb": tmdbid
			}
			},
			"progress": progress,
		}

		return self.getJSON('scrobble/%s' % action, data= data, OAuth= True, method="POST")


	# Permet de marquer un media comme Vu
	def setMediaAsWatched(self, media, tmdbid):
		return self.scrobble('stop', media, tmdbid, 100)
	


	
	# TESTS DES PARAMETRES
	def tester(self, test):
		if test == 'api':
			j = self.getTrending('movies')
		elif test == 'user':
			j = self.getUserLists()
		elif test == 'token':
			j = self.getWatchedProgress('the-last-of-us')
		
		if j is int:
			return False
		else:
			return True



	# AUTHENTIFICATION
	# Préalable : l'utilisateur a créé un compte api sur Trakt et connait api_key et client_secret
	# 3 étapes:
	# Etape 1 : Envoyer une demande à Trakt pour associer l'appli
	# getDeviceCode permet d'obtenir un devicecode, un user_code pour trakt.tv/activate
	# retour = {'device_code': 'b1aeb17d4458a594b093c2ed943838ad15a951d58ddd1c31e56905c2aa2d1d5a', 
	#			'user_code': 'B3B44310',
	#			'verification_url': 'https://trakt.tv/activate',
	#			'expires_in': 600, 
	#			'interval': 5}
	def getDeviceCode(self):
		data = {
			"client_id" : self.TRAKT_KEY
		}
	
		return self.getJSON('oauth/device/code', data= data, OAuth= False, method="POST")

	# Etape 2 : L'utilisateur doit aller sur trakt.tv/activate et saisir le user_code



	# Etape 3 : Une fois que l'utilisateur a activé le user_code alors on peut obtenir le Bearer avec getToken

	# retour = {  	
	# 				"access_token": "dbaf9757982a9e738f05d249b7b5b4a266b3a139049317c4909f2f263572c781",
  	#				"token_type": "bearer",
  	#				"expires_in": 7200,
  	#				"refresh_token": "76ba4c5c75c96f6087f58a4de10be6c00b29ea1ddc3b2022ee2016d1363e3a7c",
  	#				"scope": "public",
  	#				"created_at": 1487889741
	#			}
	def getToken(self, devicecode, secret):
		data = {			
			"code": devicecode,
			"client_id" : self.TRAKT_KEY,
			"client_secret" : secret
		}
		headers = {
			'Content-Type': 'application/json'
		}
		return self.getJSON('oauth/device/token', data= data, OAuth= False, headers= headers, method="POST")






# EXEMPLE D'UTILISATION DE myTrakt
parametres = {
	"username" 		: "zrdoctornono",
	"api_key"  		: "a4d2192a18766f2030ae4cd8f7086f1519c26c6c3d697e3e093b6ee2effbaded",
	"client_secret" : "53584c4cb9f19418ed459c5710aaf8886a9bee1f8632c0b6630d763799676b58",
	"access_token" 	: "0fc72209e8730aabdc29793df3b59b69be2b9273b89cb95d98f4ba0f6f2fa6b0",
	"refresh_token" : "6583b1502f8d79a0eed03c015b24abcfa26de4bf69a03cac307281d93c3fa23c",
	"expire" 		: 1689343342
}

mytrakt = myTrakt(parametres)
# Connatre toutes les séries vus ou commencées
"""	
shows = mytrakt.getWatched('shows')

for show in shows:
	print(str(show))
	print('-----------------------La série %s , tmdb = %s, ----------%s' % (show['show']['title'], show['show']['ids']['tmdb'], str(show['seasons'])))
	for saison in show['seasons']:
		print('a vu les episodes de la saison %s' % (saison['number']))
		for episodes in saison['episodes']:
			print('episode %s' % (episodes['number']))
	#items = mytrakt.getWatchedProgress()
	#print(str(items))
	#for item in items:

col = mytrakt.getCollection('movies')	
for film in col:
	print(film['movie']['title'])
mytrakt.addMediaToCollection('movies', 842675)
"""
ids=[]

id = {
	"ids": {
		"tmdb": 842945
	}
}
ids.append(id) 

print(mytrakt.getUserStats("zrdoctornono"))
#print('--------------------'+str(mytrakt.addMediatoUserList('eventuellement', 842945, 'movies')))
#print(str(mytrakt.getList('eventuellement')))
#print(str(mytrakt.getUserLists('zrdoctornono')))
#print(mytrakt.scrobble('stop', 'movie', 2164, 100))

#print(str(mytrakt.getUserLists()))

#print(str(mytrakt.getWatchedProgress('the-last-of-us')))
