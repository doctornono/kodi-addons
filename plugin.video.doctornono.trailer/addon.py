import sys
import urllib
from urllib.parse import urlparse
from urllib import request

import json

import os.path

import xbmc
import xbmcgui
import xbmcplugin 
import xbmcaddon

from bs4 import BeautifulSoup, Tag, NavigableString
from random import *

import sqlite3
from sqlite3 import Error


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

mode = args.get('mode', None)

xbmcplugin.setContent(addon_handle, 'movies')

my_addon = xbmcaddon.Addon('plugin.video.doctornono.trailer')
profile = xbmc.translatePath( my_addon.getAddonInfo('profile'))


#MOVIEDB_KEY = "9c1662a033ca5210dc75b91e0aa9b49e"
MOVIEDB_URLAPI =  'https://api.themoviedb.org/3/'
MOVIEDB_KEY = my_addon.getSetting("key")
listesuser= my_addon.getSetting("listes")
MOVIEDB_LANGUAGE = my_addon.getSetting("langue")

class myWindow(xbmcgui.Window):
  def __init__(self):
    self.addControl(xbmcgui.ControlImage(0,0,400,300, 'D:\\photos\\2016-05-13 12.36.15 HDR.jpg'))
    self.strActionInfo = xbmcgui.ControlLabel(100, 120, 200, 200, '', 'font13', '0xFFFF00FF')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('Push BACK to quit')
    self.button0 = xbmcgui.ControlButton(350, 500, 80, 30, "HELLO")
    self.addControl(self.button0)
    self.setFocus(self.button0)

  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU:
      self.close()

  def onControl(self, control):
    if control == self.button0:
      self.message('you pushed the button')

  def message(self, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(" My message title", message)


class MyClass(xbmcgui.Window):
  def __init__(self):
    self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    self.window.setProperty('MyAddonIsRunning', 'true')
    
    self.strActionInfo = xbmcgui.ControlLabel(100, 120, 200, 200, '', 'font13', '0xFFFF00FF')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('Push BACK to quit - A to reset text')
      
  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU:
      self.close()


def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)


def loadJson(url):
    req =  urllib.request.urlopen(url)
    response = req.read()
    req.close()
    data = json.loads(response)
    return data       


def buildURLMovieDB(folder, param):
    url = MOVIEDB_URLAPI + folder + '?api_key=' + MOVIEDB_KEY + param
    return url

def buildURLIcon(image):
    return my_addon.getAddonInfo('path') + '/resources/icons/' + image


def getDataMovieDB(category, moviedbID = None, codeiso = None, page = None, q = None):
    filter = None
    if category == 'movie':
        lien = buildURLMovieDB('movie/' + moviedbID, '&language=' + MOVIEDB_LANGUAGE)
    elif category == 'cast':
        lien = buildURLMovieDB('movie/' + moviedbID + '/credits', '')
    elif category == 'genre':
        lien = buildURLMovieDB('genre/movie/list', '&language=' + MOVIEDB_LANGUAGE)
    elif category == 'videos':
        lien = buildURLMovieDB('movie/' +  moviedbID + '/videos', '&language='+codeiso)
    elif category == 'userlist':
        lien = buildURLMovieDB('list/' + moviedbID , '')

    elif category == 'prochainement':
        lien = buildURLMovieDB('movie/upcoming', '&language='+codeiso+'&page='+page)
        filter = 'results'
    elif category == 'actuellement':
        lien = buildURLMovieDB('movie/now_playing' , '&language='+codeiso+'&page='+page)
        filter = 'results'
    elif category == 'popular':
        lien = buildURLMovieDB('movie/popular' , '&language='+codeiso+'&page='+page)
        filter = 'results'
    elif category == 'bestrank':
        lien = buildURLMovieDB('movie/top_rated' , '&language='+codeiso+'&page='+page)
        filter = 'results'
    elif category == 'search':
        query = q.replace(' ', '%20')
        lien = buildURLMovieDB('search/movie' , '&language='+codeiso+'&query='+query+'&page='+page+'&include_adult=false')
        filter = 'results'       
    elif category == 'lists':
        lien = buildURLMovieDB('list/'+page, '&language='+codeiso)
        filter = 'items' 


    if filter == None:
        return loadJson(lien)
    else:
        data = loadJson(lien)
        return data[''+ filter +'']



# GESTION MOVIE

def listItemSetPictures(poster_path):
    pictures = {    
                    'thumb':   'https://image.tmdb.org/t/p/w185' + poster_path, 
                    'poster':  'https://image.tmdb.org/t/p/w500' + poster_path,
                    'fanart':  'https://image.tmdb.org/t/p/original' + poster_path
    } 
    return pictures     


def listItemSetInfo(movie, chaine_genre):
    infos = {    
                    'title': movie['title'], #.encode('utf8', 'replace'),
                    'genre' : chaine_genre,
                    'year' : movie['release_date'],
                    'rating' : movie['vote_average'],
                    'plot' : movie['overview'], #.encode('utf8', 'replace'),          
                    'originaltitle' : movie['original_title'], #.encode('utf8', 'replace'),          
                    'code' : movie['id'],           
                    'mediatype' : 'movie'
    } 
    return infos


def listItemAddFolder(label, icon, url, context = None, infos = None, pictures = None, isfolder = True, isPlayable = True):
    
    li = xbmcgui.ListItem(label)

    if isfolder == True:
        url = build_url(url)
    else:
        if isPlayable == True:
            li.setProperty('isplayable','true')

    if pictures != None:
        li.setArt(pictures)
    else:
        li.setArt({'thumb' : buildURLIcon(icon)})
        
    li.setInfo('video', infos)
    if context != None:
        li.addContextMenuItems(context) 

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = isfolder)    


def formatGenres(genres):
    chaineGenre= ''
    for genre in listeGenres['genres']:
        if genre['id'] in genres:
            chaineGenre = chaineGenre + genre['name'] + " / "
    chaineGenre = chaineGenre[:len(chaineGenre)-2]  

    return chaineGenre 

def formatGenres2(genres):
    chaineGenre= ''
    for genre in genres:
        for genrefr in listeGenres['genres']:
            if genrefr['id'] == genre['id']:
                chaineGenre = chaineGenre + genre['name'] + " / "
    chaineGenre = chaineGenre[:len(chaineGenre)-2]

    return chaineGenre 







### FAVORITES ###
def favExistXML():
    if os.path.isfile(profile+'fav.xml') == False:
        f = open(profile+'fav.xml', "w")
        f.write("<favs></favs>")
        f.close()  


def favOpenXML():
    lienimdb = 'file:' + urllib.request.pathname2url(profile + 'fav.xml')
    req =  urllib.request.urlopen(lienimdb)
    response = req.read()
    req.close()
    return response


def favSaveXML(chaine):
    f = open(profile+'fav.xml', "w")
    f.write(chaine)
    f.close()

#OK
def favAddListe(name):
    soup = BeautifulSoup(favOpenXML(), 'html.parser')
    tag = soup.new_tag('fav')
    tag['id']= randint(1,1000000)
    tag['name'] = name
    soup.favs.append(tag)
    favSaveXML(soup.prettify())

#OK
def favDelListe(id):
    soup = BeautifulSoup(favOpenXML(), 'html.parser')
    for liste in soup.find_all('fav'):
        if liste['id']== str(id):
             # supprimer le noeud
            liste.extract()

    favSaveXML(soup.prettify())

def favRenameListe(id):
    soup = BeautifulSoup(favOpenXML(), 'html.parser')
    for liste in soup.find_all('fav'):
        if liste['id']== str(id):
             # supprimer le noeud
            #liste.extract()
            dialog = xbmcgui.Dialog()
            d = dialog.input('New list name', defaultt=liste['name'], type=xbmcgui.INPUT_ALPHANUM)
            liste['name']= d

    favSaveXML(soup.prettify())


def favAddFav(idlist, idmovie, idtrailer, name, key):
    soup = BeautifulSoup(favOpenXML(), 'html.parser')
    tag = soup.new_tag('trailer')
    tag['idtrailer']= idtrailer
    tag['idmovie']= idmovie
    tag['key']= key
    tag.string= name

    for link in soup.findAll('fav'):
        if link['id'] == idlist:
           link.insert(0, tag) 
    favSaveXML(soup.prettify())


def favDelFav(id):
    soup = BeautifulSoup(favOpenXML(), 'html.parser')
    for liste in soup.find_all('trailer'):
        if liste['idtrailer']==id:
            # supprimer le noeud
            liste.extract()     
    
    favSaveXML(soup.prettify())



def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")

    rows = cur.fetchall()

    for row in rows:
        print(row)

#debut
favExistXML()
listeGenres = getDataMovieDB('genre')

#home
if mode is None:

    listItemAddFolder('Actuellement', 'films.png', {'mode': 'actuellement', 'page' : '1'})
    listItemAddFolder('Prochainement', 'films_annees.png', {'mode': 'prochainement', 'page' : '1'})
    listItemAddFolder('Populaire', 'films_news.png', {'mode': 'popular', 'page' : '1'})
    listItemAddFolder('Top Rated', 'films_views.png', {'mode': 'bestrank', 'page' : '1'})
    listItemAddFolder('Search', 'search.png', {'mode': 'search', 'page' : '1'})

    #gestion des listes personnelles de movieDB
    tabliste = listesuser.split('|')
    for item in tabliste:
            data = getDataMovieDB('userlist', item)
            listItemAddFolder(data['name'], 'listes.png', {'mode': 'lists', 'page' : item})

    # gestion des favoris
    soup = BeautifulSoup(favOpenXML())
    for link in soup.findAll('fav'):
        listItemAddFolder(link['name'], 'star.png', {'mode': 'favorites', 'page' : link['id']}, 
                        [ ('Delete list', 'RunPlugin(%s?mode=removelist&id=%s)' % (base_url, link['id'])),  ('Rename list', 'RunPlugin(%s?mode=renamelist&id=%s)' % (base_url, link['id'])) ])           

    # creer liste de favoris
    listItemAddFolder('Add Personal List', 'star.png',  build_url({'mode': 'addlist'}), None, None, None, False, False)

    listItemAddFolder('Add Smart List', 'search.png', build_url({'mode': 'addsmartlist'}), None, None, None, False, False)
    
    database = r"D:\Bibliothèque\metadata.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
      

        print("2. Query all tasks")
        select_all_tasks(conn)


#elif mode[0] == 'prochainement' or mode[0] == 'actuellement' or mode[0] == 'popular' or mode[0] == 'bestrank' or  mode[0] == 'lists'  or  mode[0] == 'search':
elif mode[0] in ['prochainement','actuellement' ,'popular' , 'bestrank' , 'lists'  ,'search']:
    
    page = args['page'][0]

    # gestion de Search
    d = ''
    if mode[0] == 'search':
        dialog = xbmcgui.Dialog()
        d = dialog.input('Votre recherche', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
    

    data = getDataMovieDB(mode[0], page= page, q= d, codeiso = MOVIEDB_LANGUAGE)       
    for item in data:

        chaineGenre =  formatGenres(item['genre_ids'])

        infos = listItemSetInfo(item, chaineGenre)
        pictures = None
        if item['poster_path'] != None:
            pictures = listItemSetPictures(item['poster_path'])

        listItemAddFolder(item['title'], '', {'mode': 'trailer', 'action':item['id']}, None, infos, pictures)

    if mode[0] != 'lists':
        listItemAddFolder('Next', 'next.png', {'mode': mode[0], 'page' : str(int(page) + 1)})



elif mode[0] == 'trailer':

    mId = args['action'][0]

    data2 = getDataMovieDB('movie', mId)

    chaineGenre2 = formatGenres2(data2['genres'])

    infos = listItemSetInfo(data2, chaineGenre2)

    dataFR = getDataMovieDB('videos', mId, MOVIEDB_LANGUAGE)

    if MOVIEDB_LANGUAGE != 'en-US':
        dataUS = getDataMovieDB('videos', mId, 'en-US')
        data = dataFR['results']
        for item in dataUS['results']:
            data.append(item)

    for item in data:
        if item['site']=='YouTube' and (item['type'] == 'Trailer' or item['type']== 'Teaser'):

            url = 'plugin://plugin.video.youtube/play/?video_id=' + item['key']
            nom = item['name']+ " [" + str(item['size']) + "p]"

            if data2['poster_path'] != None:
                pictures = listItemSetPictures(data2['poster_path']) 

            listItemAddFolder(nom, '', url.encode('utf8', 'replace'),
                             [('Add to List', 'RunPlugin(%s?mode=addfav&mid=%s&name=%s&key=%s&idtrailer=%s)' % (base_url, mId, urllib.parse.quote(nom), item['key'], item['id'] )) ], 
                              infos, pictures, False, True)




elif mode[0] == 'favorites':
    idlist = args['page'][0]
    soup = BeautifulSoup(favOpenXML())
    for link in soup.findAll('fav'):
        
        if link['id'] == idlist:
            for fav in link.findAll('trailer'):
                url = 'plugin://plugin.video.youtube/play/?video_id=' + fav['key']
                data2 = getDataMovieDB('movie', fav['idmovie'])

                chaineGenre = formatGenres2(data2['genres'])

                infos = listItemSetInfo(data2, chaineGenre)

                if data2['poster_path'] != None:
                    pictures = listItemSetPictures(data2['poster_path'])

                listItemAddFolder(fav.string, '', url.encode('utf8', 'replace'),
                                [('Remove from list', 'RunPlugin(%s?mode=removefav&id=%s)' % (base_url, fav['idtrailer']) )], 
                                 infos, pictures, False, True)





elif mode[0] == 'addlist':
    dialog = xbmcgui.Dialog()
    name = dialog.input('List Name', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
    if name != "":
        favAddListe(name)
    #actualiser la vue
    xbmc.executebuiltin('Container.Refresh')


### CONTEXT MENU ###
elif mode[0] == 'removelist':
    id = args['id'][0]
    favDelListe(id)
    #actualiser la vue
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'renamelist':
    id = args['id'][0]
    favRenameListe(id)
    #actualiser la vue
    xbmc.executebuiltin('Container.Refresh')    


elif mode[0] == 'addfav':
    soup = BeautifulSoup(favOpenXML(), 'html.parser')
    liste =[]
    for link in soup.findAll('fav'):
        liste.append(link['name'])

    dialog = xbmcgui.Dialog()
    ret = dialog.select('Kodi', liste )

    for link in soup.findAll('fav'):
        if link['name']==liste[ret]:
            id = link['id']
    mid = args['mid'][0]
    key = args['key'][0]
    idtrailer = args['idtrailer'][0]
    name = args['name'][0]

    favAddFav(id, mid, idtrailer, name, key)


elif mode[0] == 'removefav':
    id = args['id'][0]
    favDelFav(id)
    #actualiser la vue
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'addsmartlist':
    #window = xbmcgui.Window()
    #dialog = xbmcgui.Dialog()
    #name = dialog.input('List Name', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
    mydisplay = myWindow()
    mydisplay.doModal()
    del mydisplay
    #del mydisplay
    #actualiser la vue
    #xbmc.executebuiltin('Container.Refresh')

xbmcplugin.endOfDirectory(addon_handle)