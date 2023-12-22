from urllib import request, error
#from urllib import error

import json

class myFanartTV:
    def __init__(self, key):
        self.FANART_TV_KEY = key
        self.FANART_TV_URL = 'http://webservice.fanart.tv/v3/'

    def getJSON(self, url):
        url = self.FANART_TV_URL + "{}?api_key={}".format(url, self.FANART_TV_KEY)
        req = request.Request(url)

        try:
            r = request.urlopen(req)
        except error.HTTPError as e:
            return None

        content = r.read()
        r.close()
        return json.loads(content)		


    def getMovie(self, tmdbid):
        return self.getJSON('movies/%s' % (tmdbid))


    def getTV(self, tmdbid):
        return self.getJSON('tv/%s' % (tmdbid))


    def tester(self):
        return self.getJSON('movies/9341')