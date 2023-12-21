import sys
import urllib
from urllib.parse import urlparse
from urllib import request
import sqlite3
from sqlite3 import Error

import re

import xbmc
import xbmcgui
import xbmcplugin 
import xbmcaddon
import xbmcvfs




def buildURL(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def buildURLIcon(image):
    return my_addon.getAddonInfo('path') + '/ressources/icons/' + image

def buildURLCover(chemin):
    return 'D://Bibliothèques/Science-fiction/' + chemin + '/cover.jpg'

def buildURLBook(chemin, fichier, extension):
    return 'D:\\Bibliothèques\\Science-fiction\\' + chemin.replace('/', '\\') + '\\' + fichier + '.' + extension

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


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

def select_sql(sql):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    conn = create_connection(CHEMIN_BD_CALIBRE)
    cur = conn.cursor()
    cur.execute(sql)

    rows = cur.fetchall()
    
    return rows

def choixSQL(mode, id = None):
    if mode == 'parauteur':
        sql = 'SELECT id, sort FROM authors ORDER BY sort'
    elif mode == 'auteur':
        sql = ("SELECT * FROM books a, books_authors_link b, authors c WHERE b.book = a.id AND b.author = c.id AND b.author = %s ORDER BY a.sort") % id
    elif mode == 'parserie':
        sql = "SELECT id, sort FROM series ORDER BY sort"
    elif mode == 'serie':
        sql = ("SELECT * FROM books a, books_series_link b, series c WHERE b.book = a.id AND b.series = c.id AND b.series = %s ORDER BY series_index") % id
    elif mode == 'parediteur':
        sql = "SELECT id, name FROM publishers ORDER BY name"
    elif mode == 'editeur':
        sql = ("SELECT * FROM books a, books_publishers_link b, publishers c WHERE b.book = a.id AND b.publisher = c.id AND b.publisher = %s ORDER BY name") % id
    elif mode == 'parcollection':
        sql = ""
    elif mode == 'collection':
        sql =   ""
    elif mode == 'paretiquette':
        sql = "SELECT id, name FROM tags ORDER BY name"
    elif mode == 'etiquette':
        sql = ("SELECT * FROM books a, books_tags_link b, tags c WHERE b.book = a.id AND b.tag = c.id AND b.tag = %s ORDER BY name") % id
  
    
    
    
    
    
    
    return select_sql(sql)









def listItemAddFolder(label, icon, url, context = None, infos = None, pictures = None, isfolder = True, isPlayable = True):
    
    li = xbmcgui.ListItem(label)

    if isfolder == True:
        url = buildURL(url)
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

def listItemAddBook(row):

    li = xbmcgui.ListItem(str(row[1]))

    path = row[9]
    liens = select_sql('SELECT name, format FROM data WHERE book =' + str(row[0]))
    for lien in liens:
        extension = lien[1]
        fichier = lien[0]

    url = buildURL({'mode': 'player', 'epub' : buildURLBook(path, fichier, extension)})
    
    li.setProperty('isplayable','false')
    li.setArt({'thumb' : buildURLCover(row[9]), 'poster' : buildURLCover(row[9])})

    infos = listItemSetInfo(row)

    li.setInfo('video', infos)

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = False)    



def listItemSetInfo(book):
    idbook = book[0]
    title = book[1]
    tags   = select_sql("SELECT a.name FROM tags a, books_tags_link b WHERE a.id = b.tag AND b.book = " + str(idbook))
    strtags = ' '
    for tag in tags:
        strtags += ' ' + str(''.join(tag))
    
    year = book[4]
    rating = 3
    
    desc = select_sql("SELECT text FROM comments WHERE book = " + str(idbook))
    if not desc:
        desc = ''
    else:
        desc = desc[0]
        desc = cleanhtml(str(desc[0]))

    author = book[6]

    infos = {    
            'title': title,
            'tagline' : 'serie et tome',
            'genre' : strtags,
            'year' : year,
            'rating' : rating,
            'plot' : desc,
            'director' : author,
            'code' : idbook,           
            'mediatype' : 'movie'
    } 
    return infos    
######################################
# SETTINGS
######################################

CHEMIN_BD_CALIBRE = r"D:\Bibliothèques\Science-fiction\metadata.db"
PLAYER = 'C:\\Program Files\\Calibre2\\ebook-viewer.exe'

#
#dialog = xbmcgui.Dialog()
#name = dialog.notification('Info', 'Hello World!')

my_addon = xbmcaddon.Addon('plugin.video.doctornono.books')
print(str(sys.argv))
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
xbmcplugin.setContent(addon_handle, 'movies')


### ACCUEIL ###
if mode is None:
    listItemAddFolder('En cours de lecture',    'open-book.png',    {'mode': 'encours'})
    listItemAddFolder('Rechercher',             'search.png',       {'mode': 'rechercher'})
    listItemAddFolder('Derniers ajouts',        'films.png',        {'mode': 'derniersajouts'})
    listItemAddFolder('Par auteur',             'auteur.png',       {'mode': 'parauteur'})
    listItemAddFolder('Par série',              'serie.png',        {'mode': 'parserie'})
    listItemAddFolder('Par éditeur',            'publisher.png',    {'mode': 'parediteur'})
    listItemAddFolder('Par collection',         'biblio.png',       {'mode': 'parcollection'})
    listItemAddFolder('Par étiquette',          'tags.png',         {'mode': 'paretiquette'})

elif mode[0] == 'encours':
    listItemAddFolder('a Faire', 'films.png', {'mode': 'actuellement', 'page' : '1'})
elif mode[0] == 'parcollection':
    listItemAddFolder('a Faire', 'films.png', {'mode': 'actuellement', 'page' : '1'})
elif mode[0] == 'rechercher':
    listItemAddFolder('a Faire', 'films.png', {'mode': 'actuellement', 'page' : '1'})    

### AFFICHE LA LISTE DE TOUS LES AUTEURS OU DE TOUTES LES SERIES OU DE TOUS LES EDITEURS OU DE TOUTES LES ETIQUETTES
elif mode[0] in ['parauteur', 'parserie', 'parediteur', 'paretiquette']:
    rows = choixSQL(mode[0])
    for row in rows:
        listItemAddFolder(str(row[1]),          'films.png',        {'mode': mode[0].replace('par',''), 'id': row[0]})

### AFFICHE LES LIVRES D'UN AUTEUR PARTICULIER OU D'UNE SERIE OU D'UN EDITEUR OU D'UNE ETIQUETTE
elif mode[0] in ['auteur', 'serie', 'editeur', 'etiquette']:
    id = args['id'][0]
    rows = choixSQL(mode[0], id)
    for row in rows:
        listItemAddBook(row)

### OUVRE LE LIVRE DANS L'APPLICATION CHOISIE
elif mode[0] == 'player':
    epub = args['epub'][0]
    import subprocess
    subprocess.call([PLAYER, epub])


xbmcplugin.endOfDirectory(addon_handle)