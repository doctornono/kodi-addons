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

def selectSQL(sql):
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
    if mode == 'encours':
        sql = ''
    elif mode == 'rechercher':
        sql = "SELECT * FROM books WHERE title LIKE '%" + id + "%'"
    elif mode == 'derniersajouts':
        sql = "SELECT * FROM books ORDER BY timestamp DESC LIMIT 100"       
    elif mode == 'parauteur':
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
        sql = "SELECT * FROM custom_column_1 ORDER BY value"
    elif mode == 'collection':
        sql =  ("SELECT * FROM books a, books_custom_column_1_link b, custom_column_1 c WHERE b.book = a.id AND b.value = c.id AND b.value = %s ORDER BY extra") % id
    elif mode == 'paretiquette':
        sql = "SELECT id, name FROM tags ORDER BY name"
    elif mode == 'etiquette':
        sql = ("SELECT * FROM books a, books_tags_link b, tags c WHERE b.book = a.id AND b.tag = c.id AND b.tag = %s ORDER BY name") % id
  

    elif mode == 'epub':
        sql = 'SELECT name, format FROM data WHERE book =' + id
    elif mode == 'tagbook':
        sql = "SELECT a.name FROM tags a, books_tags_link b WHERE a.id = b.tag AND b.book = " + id
    elif mode == 'descbook':
        sql = "SELECT text FROM comments WHERE book = " + id
    

    
    
    
    
    return selectSQL(sql)









def listItemAddFolder(label, icon, url):
    
    li = xbmcgui.ListItem(label)
    url = buildURL(url)
    li.setArt({'thumb' : buildURLIcon(icon)})

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = True)    



def listItemAddBook(row):

    li = xbmcgui.ListItem(str(row[1]))

    path = row[9]
    liens = choixSQL('epub', str(row[0]))
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
    tags   = choixSQL('tagbook', str(idbook))
    strtags = ' '
    for tag in tags:
        strtags += ' ' + str(''.join(tag))
    
    year = book[4]
    rating = 3
    
    desc = choixSQL('descbook', str(idbook))
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



my_addon = xbmcaddon.Addon('plugin.video.doctornono.books')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
xbmcplugin.setContent(addon_handle, 'movies')


### ACCUEIL ###
if mode is None:
    listItemAddFolder('En cours de lecture',    'star.png',         {'mode': 'encours'})
    listItemAddFolder('Rechercher',             'rechercher.png',   {'mode': 'rechercher'})
    listItemAddFolder('Derniers ajouts',        'last.png',         {'mode': 'derniersajouts'})
    listItemAddFolder('Par auteur',             'auteur.png',       {'mode': 'parauteur'})
    listItemAddFolder('Par série',              'serie.png',        {'mode': 'parserie'})
    listItemAddFolder('Par éditeur',            'editeur.png',      {'mode': 'parediteur'})
    listItemAddFolder('Par collection',         'collection.png',   {'mode': 'parcollection'})
    listItemAddFolder('Par étiquette',          'etiquette.png',    {'mode': 'paretiquette'})

### A FAIRE ###
elif mode[0] == 'encours':
    listItemAddFolder('a Faire', 'films.png', {'mode': 'actuellement'})





### AFFICHE LES 100 DERNIERS LIVRES AJOUTES DANS CALIBRE
elif mode[0] == 'derniersajouts':
    rows = choixSQL(mode[0])
    for row in rows:
        listItemAddBook(row)

### AFFICHE LA LISTE DE TOUS LES AUTEURS OU DE TOUTES LES SERIES OU DE TOUS LES EDITEURS OU DE TOUTES LES ETIQUETTES OU DE TOUTES LES COLLECTIONS
elif mode[0] in ['parauteur', 'parserie', 'parediteur', 'paretiquette', 'parcollection']:
    rows = choixSQL(mode[0])
    nomcourt = mode[0].replace('par','')
    for row in rows:
        listItemAddFolder(str(row[1]),          nomcourt + '.png',        {'mode': nomcourt, 'id': row[0]})


### AFFICHE LES LIVRES D'UN AUTEUR PARTICULIER OU D'UNE SERIE OU D'UN EDITEUR OU D'UNE ETIQUETTE OU D'UNE COLLECTION
### AFFICHE LES RESULTATS DE LA RECHERCHE
elif mode[0] in ['auteur', 'serie', 'editeur', 'etiquette', 'collection', 'rechercher']:
    if mode[0] == 'rechercher':
        dialog = xbmcgui.Dialog()
        id =  dialog.input('Votre recherche', defaultt='', type=xbmcgui.INPUT_ALPHANUM)
    else:        
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