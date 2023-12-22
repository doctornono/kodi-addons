import urllib
import json
from urllib import request
from urllib import parse


class myUptobox:
    def __init__(self, key):
        self.UPTOBOX_KEY = key
        self.UPTOBOX_LIMIT = '100'
        self.UPTOBOX_ORDER = 'file_name'
        self.UPTOBOX_LINK = 'https://uptobox.com/api/user/files?token=%s' % (self.UPTOBOX_KEY)

        self.UPTOBOX_FOLDER_MOVIE = '//movies'
        self.UPTOBOX_FOLDER_TVSHOW = '//tvshow'
        self.UPTOBOX_FOLDER_ADD = '//'

    def getRequestGET(self, lien):
        req = request.Request(lien, method = "GET") 
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0")
        r = request.urlopen(req)
        content = r.read()
        content = json.loads(content)
        r.close()
        return content

    def getRequest(self, methode , lien, data = {}):
        req = request.Request(lien)
        req.method = methode
        req.data =  bytes(json.dumps(data), encoding='utf8')
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0")
        r = request.urlopen(req)
        content = r.read()
        content = json.loads(content) 
        r.close()   
        return content


    def getFiles(self, id = '', media = 'movie'):
        if media == 'movie':        folder = self.UPTOBOX_FOLDER_MOVIE
        if media == 'tvshow':       folder = self.UPTOBOX_FOLDER_TVSHOW
        if media == 'transfert':    folder = self.UPTOBOX_FOLDER_ADD
        if id != '' : folder = folder + '/' + str(id)

        lien = '%s&path=%s&limit=%s&orderBy=%s' % (self.UPTOBOX_LINK, urllib.parse.quote(folder), self.UPTOBOX_LIMIT,  self.UPTOBOX_ORDER)

        return self.getRequestGET(lien)


    def getTree(self, media = ''):
        folder = ''
        if media == 'movie':        folder = self.UPTOBOX_FOLDER_MOVIE
        if media == 'tvshow':       folder = self.UPTOBOX_FOLDER_TVSHOW
        if media == 'transfert':    folder = self.UPTOBOX_FOLDER_ADD
          
        r = self.getFiles('', 'movie')
        data = r['data']
        liste = data['folders']
        arbo = []
        for folder in liste:
            req=self.getFiles(folder['name'])
            files = req['data']
            files = files['files']
            
            mondict = {}
            mondict['folder'] = folder
            mondict['files'] = files
            arbo.append(mondict)
        return arbo


    def getFolderID(self, path, foldername):
        r = self.getFiles(path,'movie')
        flds = r['data']
        folders = flds['folders']
        folderid=''
        for folder in folders:
            if folder['name'] == str(foldername.replace(u'\xa0', u'')):
                folderid = folder['fld_id']
        return folderid


    def createFolder(self, path, foldername):
        data = {
            'path' : path,
            'name' : foldername.replace(u'\xa0', u'')
        }
        return self.getRequest("PUT", self.UPTOBOX_LINK, data)


    def deleteFolder(self, fld_id):
        data = {
            'fld_id' : fld_id
        }
        return self.getRequest("DELETE", self.UPTOBOX_LINK, data)


    def deleteFile(self, file_id):
        data = {
            'file_codes' : file_id
        }
        return self.getRequest("DELETE", self.UPTOBOX_LINK, data)


    def moveFile(self, fileId, destinationFolderId):
        data = {
            'file_codes' : fileId,
            'destination_fld_id' :destinationFolderId,
            'action' : 'move'
        }
        return self.getRequest("PATCH", self.UPTOBOX_LINK, data)


    def addFile(self, fileID):
        # fileID correspond à l'ID de l'url ex: https://uptobox.com/1y4uut5trbd7
        lien = 'https://uptobox.com/api/user/file/alias?token=%s&file_code=%s' % (self.UPTOBOX_KEY, fileID)
        return self.getRequestGET(lien)


    def setFileDescription(self, fileID, tmdbID):
        data = {
            'file_code' : fileID,
            'description' :tmdbID,
        }
        return self.getRequest("PATCH", self.UPTOBOX_LINK, data)




    def importMovie(self, file_code, tmdbid, foldername):
        self.setFileDescription(file_code,tmdbid)
        self.createFolder(self.UPTOBOX_FOLDER_MOVIE, foldername)
        folderid = self.getFolderID('', foldername)
        if folderid != '':
            self.moveFile(file_code, folderid)
            print('[MyUptobox]***** Le film %s - %s  a été importé' % (file_code, foldername))       



    def searchTitle(self, title, year = ''):
        MOVIEDB_KEY = "9c1662a033ca5210dc75b91e0aa9b49e"
        MOVIEDB_LANGUAGE = 'fr-FR'
        if year != '':
            year = '&year=' + str(year)  #+ '&primary_release_year=' + str(year)
        lien = 'https://api.themoviedb.org/3/search/movie?api_key=%s&language=%s&page=1&include_adult=false&query=%s%s' % (MOVIEDB_KEY, MOVIEDB_LANGUAGE,urllib.parse.quote(title), year)
        return self.getRequestGET(lien)

    """
    def searchID(self, id):
        MOVIEDB_KEY = "9c1662a033ca5210dc75b91e0aa9b49e"
        MOVIEDB_LANGUAGE = 'fr-FR'
        lien = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s' % (str(id) ,MOVIEDB_KEY, MOVIEDB_LANGUAGE)
        return self.getRequestGET(lien)
"""

    # ///////////////// MAInTENANCE /////////////////
    def restoreAllFiles(self):
        data = self.getFiles('', 'transfert')
        destinationFolderId = data['data']['currentFolder']['fld_id']
        
        arbo = self.getTree('movie')
        filesId = []
        for item in arbo:
            for file in item['files']:
                filesId.append(file['file_code'])
        s = ",".join([str(i) for i in filesId])

        data = {
            'file_codes' : s,
            'destination_fld_id' : destinationFolderId,
            'action' : 'move'
        }
        return self.getRequest("PATCH", self.UPTOBOX_LINK, data)        


    def check(self):
        arbo = self.getTree('movie')
        self.checkUnusedFolders(arbo)
        self.checkMultipleFile(arbo)
        #self.checkTMDBId(arbo)

         
    def checkUnusedFolders(self, arbo = []):
        if arbo == [] :
            arbo = self.getTree('movie')
        for movie in arbo:
            folder =  movie['folder']
            if len(movie['files']) == 0:
                print('[MyUptobox]***** Le dossier %s - %s n a pas de fichiers et a été supprimé' % (folder['fld_id'], folder['fld_name']))
                self.deleteFolder(folder['fld_id'])  


    def checkMultipleFile(self, arbo = []):
        if arbo == [] :
            arbo = self.getTree('movie')
        for movie in arbo:
            files  =  movie['files']
            dicts = []
            if len(files) > 1:
                for file in files:
                    dict = {'name' : file['file_name'], 'size' : file['file_size']}
                    if dict in dicts:
                        print('[MyUptobox]***** %s est un doublon et a été supprimé' % file['file_name'])
                        self.deleteFile(file['file_code'])
                    else:
                        dicts.append(dict)


    def checkTMDBId(self, arbo = []):
        if arbo == [] :
            arbo = self.getTree('movie')
        for movie in arbo:
            folder =  movie['folder']
            files  =  movie['files']

            tmdbid = 0
       
            for file in files:
                if file['file_descr'] == '':
                    if tmdbid == 0:
                        title = folder['name'].split(' (')[0]
                        year = folder['name'].split('(')[1].split(')')[0]     
                        tmdb = self.searchTitle(title, year)
                        if tmdb['total_results'] == 1:
                            tmdbid = tmdb['results'][0]['id']
                            self.setFileDescription(file['file_code'], tmdbid)
                            print('[MyUptobox]+++++ Le fichier %s n avait pas de tmdbid %s'  % (file['file_name'], tmdbid))
                    else:
                        print('[MyUptobox]+++++ Le fichier %s n a pas de tmdbid %s'  % (file['file_name'], tmdbid))





# ---------- NE MARCHE PAS ---------------------------
    def setFolderDescription(self, fileID, tmdbID):
        data = {
           # 'token' : self.UPTOBOX_KEY,
            'fld_id' : fileID,
            'description' :tmdbID
        }
        
        return self.getRequest("PATCH", self.UPTOBOX_LINK, data)




""" 
UPTOBOX_KEY = "cc926cba80b1e85aefd91c3245a6794d8qcql"
u2b = myUptobox(UPTOBOX_KEY)

u2b.checkTMDBId()

#print(u2b.getFiles('', 'movie'))
u2b.addFile('ymzey5ax8i38')

r = u2b.getFiles(media = 'movie')  
folders = r['data']
movies  = folders['folders']
movies.sort(key=lambda x: x["name"])
for item in movies:
    print('++++++++++++++++'+ str(item['name']), '++++++++++++++++++++++' , unidecode.unidecode(item['name']))
"""
