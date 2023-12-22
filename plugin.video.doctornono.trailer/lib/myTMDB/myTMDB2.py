from urllib import request
from urllib import error

import json

class myTMDB2:
	def __init__(self, parametres):
		# Constantes
								
		self.TMDB_URLAPI 		= 'https://api.themoviedb.org/3/'

		self.setParameters(parametres)


	def setParameters(self, parametres):
		# Variables User
		self.TMDB_KEY 			= parametres["api_key"]		
		self.TMDB_USERNAME 	= parametres["username"] 	
		# Variables Authentification
		self.TMDB_SECRET 		= parametres["client_secret"] 
		self.TMDB_BEARER 		= parametres["access_token"]
		self.TMDB_REFRESH_TOKEN= parametres["refresh_token"]
		self.TMDB_EXPIRE		= parametres["expire"]		


	def getParameters(self):
		parametres = {
			"username" 		: self.TMDB_USERNAME,
			"api_key"  		: self.TMDB_KEY,
			"client_secret" : self.TMDB_SECRET,
			"access_token" 	: self.TMDB_BEARER,
			"refresh_token" : self.TMDB_REFRESH_TOKEN,
			"expire" 		: self.TMDB_EXPIRE
		}

		return parametres


	def getHeaders(self):
		headers = {
			'Content-Type'		: 'application/json',
			'TMDB-api-version'	: self.TMDB_API_VERSION,
			'TMDB-api-key'		: self.TMDB_KEY
		}		

		return headers

	
	# Appelle l'API  et retourne le JSON
	# method : GET, POST, PUT
	# OAuth = True pour utiliser l'access token
	def getJSON(self, url, method = "GET", data = False, OAuth = False, headers = False):
		if headers is False:
			headers = self.getHeaders()

		req = request.Request('%s/%s' % (self.TMDB_URLAPI, url), method = method, headers = headers)
		if OAuth is True:
			req.add_header('Authorization', 'Bearer ' + self.TMDB_BEARER)
		
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




