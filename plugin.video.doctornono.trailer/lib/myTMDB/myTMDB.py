import os
import sys

import urllib
from urllib import request, error, parse
from urllib.error import HTTPError

import json
from datetime import datetime

from bs4 import BeautifulSoup
import sqlite3
from lib.myFanartTV import myFanartTV

class myTMDB:
	def __init__(self, parametres):
		self.MOVIEDB_URLAPI = 'https://api.themoviedb.org/3/'
		self.setParameters(parametres)


	def setParameters(self, parametres):
		self.MOVIEDB_KEY 			= parametres["api_key"]	  									# "9c1662a033ca5210dc75b91e0aa9b49e"
		self.MOVIEDB_LANGUAGE 		= parametres["langue"]  							# 'fr-FR'
		self.MOVIEDB_USERNAME 		= parametres["username"]								# doctornono
		self.MOVIEDB_USERPASSWORD 	= parametres["password"]						# cousin
		self.MOVIEDB_TOKEN 			= parametres["token"]	
		self.MOVIEDB_SESSION_ID 	= parametres["session_id"]	
		self.MOVIEDB_USER_ID 		= parametres["user_id"]
		self.MOVIEDB_SQL_PATH 		= parametres["sql_path"]


	"""
		*** Prépare l'URL pour l'API
		url = 'https://api.themoviedb.org/3/' + folder + '?api_key=9c1662a033ca5210dc75b91e0aa9b49e' + param
	"""
	def buildURLMovieDB(self, folder, param):
		return self.MOVIEDB_URLAPI + "{}?api_key={}{}".format(folder, self.MOVIEDB_KEY, param)


	"""
		*** Appelle l'API GET et retourne le JSON
	"""
	def loadJson(self, url):
		try:
			req = urllib.request.urlopen(url)
			response = req.read()
			req.close()
			data = json.loads(response)
			return data
		except:
			pass
		return None

	"""
		*** Appelle l'API POST et retourne le JSON
	"""
	def loadJsonPost(self, url, data):

		req = request.Request(url, method = "POST")
		req.add_header('Content-Type', 'application/json')
		data = json.dumps(data)
		data = data.encode()
		r = request.urlopen(req, data=data)
		content = r.read()
		r.close()
		data = json.loads(content)

		return data
		
	# TESTS DES PARAMETRES
	def tester(self, test):
		if test == 'api':
			j = self.getMovies('popular')
		elif test == 'user':
			j = self.getUserLists()
		elif test == 'token':
			j = self.getWatchedProgress('the-last-of-us')
		
		if j is None:
			return False
		else:
			return True

	"""
	*********************************
	************* SQL LITE
	*********************************		
	"""
	def databasePathSQL(self):

		#path = os.path.dirname(os.path.abspath(__file__))
		return os.path.join(self.MOVIEDB_SQL_PATH, 'data.db')


	def checkDatabaseExistSQL(self):

		return os.path.exists(self.databasePathSQL())


	def createDatabaseSQL(self):

		con = sqlite3.connect(self.databasePathSQL()) 
		cur = con.cursor()
		# creation des tables
		cur.execute('CREATE TABLE IF NOT EXISTS "keys" (		"key"	TEXT,	"value"	BLOB,	"date_scrap"	INTEGER,	PRIMARY KEY("key"))')
		cur.execute('CREATE TABLE IF NOT EXISTS "movies" (	"tmdbid"	INTEGER,	"jsontmdb"	BLOB,	"date"	INTEGER,	PRIMARY KEY("tmdbid"))')
		cur.execute('CREATE TABLE IF NOT EXISTS "tvshows" (	"tmdbid"	INTEGER,	"jsontmdb"	BLOB,	"date"	INTEGER,	PRIMARY KEY("tmdbid"))')
		cur.execute('CREATE TABLE IF NOT EXISTS "uptobox" (	"fld_id"	TEXT,	"tmdbid"	INTEGER,	"fld_name"	TEXT,	PRIMARY KEY("fld_id"))')
		# insertion
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('imdb_top250', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('imdb_top250_tvshow', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('tmdb_movies_watchlist', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('tmdb_movies_rated', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('tmdb_movies_favorites', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('tmdb_tvshow_watchlist', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('tmdb_tvshow_rated', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('tmdb_tvshow_favorites', 1)")
		cur.execute("INSERT INTO keys (key, date_scrap) VALUES('trakt_last_activities', 1)")

		con.commit()


	def selectSQL(self, sql):

		con = sqlite3.connect(self.databasePathSQL())
		con.row_factory = sqlite3.Row
		cur = con.cursor()		
		cur.execute(sql)
		row = cur.fetchone()
		con.close()

		return row


	def selectMultipleSQL(self, sql):

		con = sqlite3.connect(self.databasePathSQL())
		con.row_factory = sqlite3.Row
		cur = con.cursor()		
		cur.execute(sql)
		rows = cur.fetchall()
		con.close()

		return rows


	def executeSQL(self, sql):

		con = sqlite3.connect(self.databasePathSQL())
		cur = con.cursor()
		cur.execute(sql)
		con.commit()
		con.close()


	def deleteTable(self, table):

		self.executeSQL("DELETE FROM %s" % (table))


	def saveMovie(self, id, j):

		row = self.selectSQL("SELECT * FROM movies WHERE tmdbid = %s " % (id))
		if isinstance(row, tuple) == False :
			j = json.dumps(j)
			j = str(j)

			self.executeSQL("INSERT INTO movies VALUES(%s,'%s',%s)" % (id, j.replace("'", "''"),datetime.now().timestamp()))


	def openMovie(self, id):

		row = self.selectSQL("SELECT * FROM movies WHERE tmdbid = %s " % (id))
		if row is None:
			return False
		else:
			return json.loads(row['jsontmdb'])
			

	def saveTVShow(self, id, j):

		row = self.selectSQL("SELECT * FROM tvshows WHERE tmdbid = %s " % (id))
		if isinstance(row, tuple) == False :
			j = json.dumps(j)
			j = str(j)

			self.executeSQL("INSERT INTO tvshows VALUES(%s,'%s',%s)" % (id, j.replace("'", "''"),datetime.now().timestamp()))


	def openTVShow(self, id):

		row = self.selectSQL("SELECT * FROM tvshows WHERE tmdbid = %s " % (id))
		if row is None:
			return False
		else:
			return json.loads(row['jsontmdb'])




	def openKey(self, key):

		row = self.selectSQL("SELECT * FROM keys WHERE key LIKE '%s'" % (key))
		if row is None:
			return False
		else:
			return json.loads(row['value'])


	def saveKey(self, key, data):

		data = json.dumps(data, indent = 4)	
		self.executeSQL("UPDATE keys SET value = '%s', date_scrap = %s WHERE key = '%s'" % (data, datetime.now().timestamp(), key))

	def addToKey(self, key, tmdbid):
		# ajout à la key favorites
		items = self.openKey(key)
		items['data'].append({"tmdb_id" : int(tmdbid)})
		self.saveKey(key, items)     


	def removeFromKey(self, key, tmdbid):
		items = self.openKey(key)
		for idx, obj in enumerate(items['data']):
			if obj['tmdb_id'] == int(tmdbid):
				items['data'].pop(idx)

		self.saveKey(key, items) 


	def updateRatingKey(self, key, tmdbid, note):
		notes = self.openKey(key)
		ex = list(filter(lambda x:x["tmdb_id"]==int(tmdbid),notes['data']))
		if ex == []:
			notes['data'].append({"tmdb_id": int(tmdbid), "userrating" : int(note) })
		else:
			ex[0]['userrating'] = int(note)
		
		self.saveKey(key, notes)    


	"""
		*** Retourne les infos d'un film

		id	:	tmdb id du film
		append_to_response : 'videos,images,credits,keywords,translations,alternative_titles,changes,external_ids,recommendations,release_dates,reviews,similar'
	"""
	def getMovie(self, id, language = None, append_to_response = 'videos,images,credits,keywords,release_dates', force = False):
		
		if language == None : language = self.MOVIEDB_LANGUAGE
		if force == False:
			movie = self.openMovie(id)
		else:
			movie = False
		if movie == False:
			lien = self.buildURLMovieDB('movie/%s' % id, '&language=%s&append_to_response=%s' % (language,  append_to_response))
			j = self.loadJson(lien)
			myfan = myFanartTV.myFanartTV('d3882f221a54e365c1187dff9ceda7fc')
			fanart = myfan.getMovie(id)
			if fanart is not None:
				j['fanarttv'] = fanart
			
			self.saveMovie(id, j)
		else:
			j= movie
		return j


	"""
		*** Retourne les films des listes TMDB
		id : 'upcoming', 'popular', 'top_rated', 'now_playing', 'latest' , 'recommendations', 'similar'

		param : {
			'language' : 'fr-FR',
			'page' : 1
			'region' : 'FR' 	#pour now_playing uniquement
			'idtmdb' : idmovieTMDB 	#pour recommendations, similar
		}
	
	"""
	def getMovies(self, id, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		if param.__contains__('page') == False :		param['page'] = 1 

		if id in ('upcoming', 'popular', 'top_rated', 'now_playing', 'latest'):
			lien = self.buildURLMovieDB('movie/%s' % (id), '&language=%s&page=%s' % (param['language'], param['page']))
		elif id in ('recommendations', 'similar'):
			lien = self.buildURLMovieDB('movie/%s/%s' % (param['idtmdb'], id), '&language=%s&page=%s' % (param['language'], param['page']))		

		return self.loadJson(lien)


	def getTrailersUS(self, id, media):

		lien = self.buildURLMovieDB('%s/%s' % (media, id), '&language=%s&append_to_response=%s' % ('en-US',  'videos'))
		return self.loadJson(lien)		


	def getPeople(self, id):

		lien = self.buildURLMovieDB('person/%s/combined_credits' % (id), '')
		return self.loadJson(lien)


	"""
		*** Retourne les résultats d'une recherche simple

		q : query string

		param : {
			'type' : 'multi', 'movie', 'tv', 'person', 'keyword', 'collection', 'company'
			'language' : 'fr-FR'
			'page' : 1
		}
	
	"""
	def getSearch(self, q, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		if param.__contains__('page') == False :		param['page'] = 1 
		if param.__contains__('type') == False :		param['type'] = 'movie'
		
		lien = self.buildURLMovieDB('search/%s' % (param['type']), '&language=%s&page=%s&query=%s' % (param['language'], param['page'], q.replace(' ', '%20')))		
		
		return self.loadJson(lien)


	"""
		*** Retourne les éléments d'une liste

		id : id de la liste

		param : {
			'language' : 'fr-FR'
		}
	"""
	def getList(self, id, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE

		lien = self.buildURLMovieDB('list/%s' % (id), '&language=%s' % (param['language']))		
		
		return self.loadJson(lien)



	"""
		*** Retourne les traductions des genres et leur ID

		category : 'movie', 'tv'

		param : {
			'language' : 'fr-FR'
		}		
	
		INUTILISE !!!
	"""
	def getGenres(self, category, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		lien = self.buildURLMovieDB('genre/%s/list' % (category), '&language=%s' % (param['language']))

		return self.loadJson(lien)			


	def getSaga(self, id, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		lien = self.buildURLMovieDB('collection/%s' % (id), '&language=%s' % (param['language']))

		return self.loadJson(lien)


	def getStudio(self, id, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		if param.__contains__('page') == False :		param['page'] = 1 
		lien = self.buildURLMovieDB('discover/movie', '&language=%s&with_companies=%s&page=%s' % (param['language'], id, param['page']))

		return self.loadJson(lien)


	def getTag(self, id, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		if param.__contains__('page') == False :		param['page'] = 1 
		lien = self.buildURLMovieDB('keyword/%s/movies' % id, '&language=%s&with_keywords=%s&page=%s' % (param['language'], id, param['page']))

		return self.loadJson(lien)



	def getIMDBTop250(self, cat = 'movie', force = False):

		if cat == 'movie':
			key = 'imdb_top250'
			url = 'https://www.imdb.com/chart/top/'
		elif cat == 'tvshow':
			key = 'imdb_top250_tvshow'
			url = 'https://www.imdb.com/chart/toptv/'

		row = self.selectSQL("SELECT * FROM keys WHERE key LIKE '%s'" % (key))
		now = datetime.now().timestamp()

		if int(row['date_scrap']) < int(now - 24*60*60*7) or force is True:
			
			req = urllib.request.urlopen(url)
			response = req.read()
			req.close()
			soup = BeautifulSoup(response, 'html.parser')
			tableau = soup.table.tbody.find_all('tr')
			top250 = {}
			top250['data'] = []
			for ligne in tableau:
				rank = ligne.select('span[name="rk"]')[0].attrs['data-value']
				imdbid = ligne.select('div[data-titleid]')[0].attrs['data-titleid']
				top250['data'].append({"rank" : rank, "imdb_id" : imdbid})

			top250 = json.dumps(top250, indent = 4)
			self.executeSQL("UPDATE keys SET value = '%s', date_scrap = %s  WHERE key LIKE '%s'" % (top250 , now, key))
			return top250
		else:
			return row['value']
			




	def userGetLists(self):

		session_id = self.userCreateSession()
		userid = self.userGetId() 
		lien = self.buildURLMovieDB('account/%s/lists' % (userid), '&session_id=%s' % (session_id))

		return self.loadJson(lien)


	def userGetMovies(self, id, page):

		session_id = self.userCreateSession()
		userid = self.userGetId() 
		lien = self.buildURLMovieDB('account/%s/%s/movies' % (userid, id), '&session_id=%s&language=%s&page=%s' % (session_id, self.MOVIEDB_LANGUAGE, page))		

		return self.loadJson(lien)


	def userGetAllMovies(self, cat, force = False):

		if cat == 'watchlist' : 	key = 'tmdb_movies_watchlist'
		if cat == 'favorite' : 		key = 'tmdb_movies_favorites'
		if cat == 'rated' : 		key = 'tmdb_movies_rated'

		row = self.selectSQL("SELECT * FROM keys WHERE key LIKE '%s'" % (key))
		now = datetime.now().timestamp()

		if int(row['date_scrap']) < int(now - 24*60*60*7) or force is True:
			mylists = self.userGetMovies(cat, 1)
			nbpage = int(mylists['total_pages'])
			results = mylists['results']
			for i in range(1, nbpage):
				i = i + 1
				re = self.userGetMovies(cat, i)
				results = results + re['results']

			watchlist = {}
			watchlist['data'] = []
			for movie in results:
				if cat == 'rated':
					watchlist['data'].append({"tmdb_id" : movie['id'], "userrating" : movie['rating']})
				else:
					watchlist['data'].append({"tmdb_id" : movie['id']})

			watchlist = json.dumps(watchlist, indent = 4)
			self.executeSQL("UPDATE keys SET value = '%s', date_scrap = %s  WHERE key LIKE '%s'" % (watchlist , datetime.now().timestamp(), key))
		
			return watchlist
		else:
			return row['value']	




	"""
	///////////////// GESTION USER & AUTHENTIFICATION ///////////////////////
	"""
	def userCreateRequestToken(self):

		lien = self.buildURLMovieDB('/authentication/token/new', '')
		token = self.loadJson(lien)	
		self.MOVIEDB_TOKEN = token["request_token"]

		return 	token["request_token"]


	def userAuthoriseRequestTokenWithLogin(self):
		"""
		This method allows an application to validate a request token by entering a username and password.
		"""
		token = self.userCreateRequestToken()
		data = {
			"username": self.MOVIEDB_USERNAME,
			"password": self.MOVIEDB_USERPASSWORD,
			"request_token": token
		}

		lien = self.buildURLMovieDB('authentication/token/validate_with_login', '')	

		req = request.Request(lien, method="POST")
		req.add_header('Content-Type', 'application/json')
		data = json.dumps(data)
		data = data.encode()
		r = request.urlopen(req, data=data)
		
		return token


	def userCreateSession(self):

		token = self.userAuthoriseRequestTokenWithLogin()
		data = {
			"request_token": token
		}

		lien = self.buildURLMovieDB('authentication/session/new', '')	

		req = request.Request(lien, method="POST")
		req.add_header('Content-Type', 'application/json')
		data = json.dumps(data)
		data = data.encode()
		r = request.urlopen(req, data=data)
		content = r.read()
		content =  json.loads(content)
		self.MOVIEDB_SESSION_ID = content['session_id']

		return content['session_id']	


	def userGetId(self):

		if self.MOVIEDB_USER_ID == '':
			session_id = self.userCreateSession()
			lien = self.buildURLMovieDB('account', '&session_id=%s' % (session_id))		
			rep = self.loadJson(lien)
			self.MOVIEDB_USER_ID = rep['id']

		return self.MOVIEDB_USER_ID		

	"""
	//////////////// FIN USER //////////////////////////////
	"""




	"""
	//////////////// UPTOBOX //////////////////////////////
	"""
	def saveUptoboxFolder(self, fld_id, tmdbid, fld_name):

		self.executeSQL("INSERT INTO uptobox VALUES('%s', %s, '%s')" % (fld_id, tmdbid, fld_name.replace("'", "''")))


	def updateUptoboxFolderName(self, fld_id, tmdbid, fld_name):

		self.executeSQL("UPDATE uptobox SET fld_name = '%s' WHERE fld_id = '%s' AND tmdbid = %s" % (fld_name.replace("'", "''"), fld_id, tmdbid))


	def getUptoboxFolder(self, fld_id):

		row = self.selectSQL("SELECT tmdbid FROM uptobox WHERE fld_id = %s" % (fld_id))
		if row is None:
			return False
		else:
			return row['tmdbid']


	def getUptoboxFolderName(self, tmdbid):

		row = self.selectSQL("SELECT fld_name FROM uptobox WHERE tmdbid = %s" % (tmdbid))
		if row is None:
			return False
		else:
			return row['fld_name']


	def getUptoboxFolderWithoutName(self):

		rows = self.selectMultipleSQL("SELECT * FROM uptobox WHERE fld_name is NULL")
		return rows
	

	"""
	//////////////// ACTION ////////////////////////
	"""
	def createList(self, listname, listdescription):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"name": listname,
			"description": listdescription,
			"language": "fr"
		}

		lien = self.buildURLMovieDB('list', '&session_id=%s' % (session_id))	

		return self.loadJsonPost(lien, data)


	def addToList(self, id, idliste):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"media_id": id
		}

		lien = self.buildURLMovieDB('list/%s/add_item' % (idliste), '&session_id=%s' % (session_id))	
		return self.loadJsonPost(lien, data)


	def userRemoveFromList(self, idliste, id):

		session_id = self.MOVIEDB_SESSION_ID
	
		data = {
			"media_id": id
		}

		lien = self.buildURLMovieDB('list/%s/remove_item' % (idliste), '&session_id=%s' % (session_id))	
		return self.loadJsonPost(lien, data)


	def userDeleteList(self, id):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"session_id": session_id
		}

		lien = self.buildURLMovieDB('list/%s' % (id), '&session_id=%s' % (session_id))
		req = request.Request(lien)
		req.method = 'DELETE'
		req.data =  bytes(json.dumps(data), encoding='utf8')
		req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0")
		try:
			handler = request.urlopen(req)
			content = handler.read()
			content = json.loads(content) 			
		except HTTPError as e:
			content = e.read()		

		return content		


	def rateMovie(self, id, note):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"value": note
		}

		lien = self.buildURLMovieDB('movie/%s/rating' % (id), '&session_id=%s' % (session_id))
		return self.loadJsonPost(lien, data)	








	def addToWatchlist(self, id):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"media_type" : "movie",
			"media_id": id,
			"watchlist" : True
		}

		lien = self.buildURLMovieDB('account/%s/watchlist' % (self.userGetId()), '&session_id=%s' % (session_id))
		return self.loadJsonPost(lien, data)




	def addToFavorites(self, id):
		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"media_type" : "movie",
			"media_id": id,
			"favorite" : True
		}

		lien = self.buildURLMovieDB('account/%s/favorite' % (self.userGetId()), '&session_id=%s' % (session_id))
		return self.loadJsonPost(lien, data)



	def removeFromFavorites(self, id):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"media_type" : "movie",
			"media_id": id,
			"favorite" : False
		}

		lien = self.buildURLMovieDB('account/%s/favorite' % (self.userGetId()), '&session_id=%s' % (session_id))
		return self.loadJsonPost(lien, data)


	def removeFromWatchlist(self, id):

		session_id = self.MOVIEDB_SESSION_ID

		data = {
			"media_type" : "movie",
			"media_id": id,
			"watchlist" : False
		}

		lien = self.buildURLMovieDB('account/%s/watchlist' % (self.userGetId()), '&session_id=%s' % (session_id))
		return self.loadJsonPost(lien, data)


		


	"""
		*** Retourne les infos d'un tvshow

		id	:	tmdb id du tvshow
		append_to_response : 'videos,images,credits,keywords,translations,alternative_titles,changes,external_ids,recommendations,release_dates,reviews,similar'
	"""
	def getTVShow(self, id, language = None, append_to_response = 'videos,images,credits,keywords,release_dates,external_ids,content_ratings', force = False):
		
		if language == None : language = self.MOVIEDB_LANGUAGE
		if force == False:
			tvshow = self.openTVShow(id)
		else:
			tvshow = False
		if tvshow == False:
			lien = self.buildURLMovieDB('tv/%s' % id, '&language=%s&append_to_response=%s' % (language,  append_to_response))
			j = self.loadJson(lien)
			myfan = myFanartTV.myFanartTV('d3882f221a54e365c1187dff9ceda7fc')
			idtvdb = j['external_ids']['tvdb_id']
			fanart = myfan.getTV(idtvdb)
			if fanart is not None:
				j['fanarttv'] = fanart
			
			self.saveTVShow(id, j)
		else:
			j= tvshow
		return j


	def getTVShowSeason(self, id, season_number, language = None, append_to_response = 'videos,images,credits,keywords,release_dates,external_ids', force = False):
		
		if language == None : language = self.MOVIEDB_LANGUAGE
		if force == False:
			tvshow = self.openTVShow(id)
		else:
			tvshow = False
		if tvshow == False:
			lien = self.buildURLMovieDB('tv/%s/season/%s' % (id, season_number), '&language=%s&append_to_response=%s' % (language,  append_to_response))
			j = self.loadJson(lien)
		else:
			j= tvshow

		return j




	def userGetTVShows(self, id, page):

		session_id = self.userCreateSession()
		userid = self.userGetId() 
		lien = self.buildURLMovieDB('account/%s/%s/tv' % (userid, id), '&session_id=%s&language=%s&page=%s' % (session_id, self.MOVIEDB_LANGUAGE, page))		

		return self.loadJson(lien)


	def userGetAllTVShows(self, cat, force = False):
		
		if cat == 'watchlist' : 	key = 'tmdb_tvshow_watchlist'
		if cat == 'favorite' : 		key = 'tmdb_tvshow_favorites'
		if cat == 'rated' : 		key = 'tmdb_tvshow_rated'

		row = self.selectSQL("SELECT * FROM keys WHERE key LIKE '%s'" % (key))
		now = datetime.now().timestamp()

		if int(row['date_scrap']) < int(now - 24*60*60*7) or force is True:
			mylists = self.userGetTVShows(cat, 1)
			nbpage = int(mylists['total_pages'])
			results = mylists['results']
			for i in range(1, nbpage):
				i = i + 1
				re = self.userGetTVShows(cat, i)
				results = results + re['results']

			watchlist = {}
			watchlist['data'] = []
			for movie in results:
				if cat == 'rated':
					watchlist['data'].append({"tmdb_id" : movie['id'], "userrating" : movie['rating']})
				else:
					watchlist['data'].append({"tmdb_id" : movie['id']})

			watchlist = json.dumps(watchlist, indent = 4)
			self.executeSQL("UPDATE keys SET value = '%s', date_scrap = %s  WHERE key LIKE '%s'" % (watchlist , datetime.now().timestamp(), key))
		
			return watchlist
		else:
			return row['value']	




	def getTVShows(self, id, param = {}):

		if param.__contains__('language') == False : 	param['language'] = self.MOVIEDB_LANGUAGE
		if param.__contains__('page') == False :		param['page'] = 1 

		if id in ('on_the_air', 'popular', 'top_rated', 'airing_today', 'latest'):
			lien = self.buildURLMovieDB('tv/%s' % (id), '&language=%s&page=%s' % (param['language'], param['page']))
		elif id in ('recommendations', 'similar'):
			lien = self.buildURLMovieDB('tv/%s/%s' % (param['idtmdb'], id), '&language=%s&page=%s' % (param['language'], param['page']))		

		return self.loadJson(lien)
"""
parametresTMDB = {
	"username" 		: "doctornono",
	"password" 		: "cousin",
	"api_key"  		: "9c1662a033ca5210dc75b91e0aa9b49e",
	"langue" 		: 'fr-FR',
	"token"         : 'my_addon.getSetting("tmdb-token")',
	"session_id" 	: '2acd4d9106653d527823b5d5be3827174745e08e',
	"user_id"       : 'my_addon.getSetting("tmdb-user-id")',
	"sql_path" 		: ''
} 
mytmdb = myTMDB(parametresTMDB)
print(str(mytmdb.userCreateSession()))

MOVIEDB_KEY = "9c1662a033ca5210dc75b91e0aa9b49e"
MOVIEDB_LANGUAGE = 'fr-FR'
MOVIEDB_USERNAME = "doctornono"
MOVIEDB_PASSWORD = "cousin"
UPTOBOX_KEY = "cc926cba80b1e85aefd91c3245a6794d8qcql"

print(mytmdb.getGenres('movie'))
"""