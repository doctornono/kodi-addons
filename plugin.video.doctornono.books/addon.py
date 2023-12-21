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
    return my_addon.getAddonInfo('path') + '/resources/icons/' + image

def buildURLCover(chemin):
    return 'D://Bibliothèques/Science-fiction/' + chemin + '/cover.jpg'

def buildURLBook(chemin):
    return 'D://Bibliothèques/Science-fiction/' + chemin + '/cover.jpg'

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
   # , row[9], {'mode': 'player', 'chemin' : 'url'},  None, infos

    li = xbmcgui.ListItem(str(row[1]))
    url = buildURL({'mode': 'player', 'chemin' : 'url'})
    
    li.setProperty('isplayable','false')
    li.setArt({'thumb' : buildURLCover(row[9]), 'poster' : buildURLCover(row[9])})

    infos = listItemSetInfo(row)
    print(str(row))
    li.setInfo('video', infos)


    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = False)    



def listItemSetInfo(book):
    idbook = row[0]
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
        desc = cleanhtml(str(desc[0]))
    print('"""""""""""""""""""""""""""""""""', desc)
    author = book[6]

    infos = {    
            'title': title, 
            'genre' :str(strtags),
            'year' : year,
            'rating' : rating,
            'plot' : str(desc),
            'outline':'desc',
            'director' : author,
            'code' : idbook,           
            'mediatype' : 'movie'
    } 
    return infos    
######################################
# SETTINGS
######################################

CHEMIN_BD_CALIBRE = r"D:\Bibliothèques\Science-fiction\metadata.db"


#
#dialog = xbmcgui.Dialog()
#name = dialog.notification('Info', 'Hello World!')

my_addon = xbmcaddon.Addon('plugin.video.doctornono.trailer')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
xbmcplugin.setContent(addon_handle, 'movies')
### ACCUEIL ###
if mode is None:
    listItemAddFolder('En cours de lecture',    'films.png', {'mode': 'encours',        'page' : '1'})
    listItemAddFolder('Rechercher',             'films.png', {'mode': 'rechercher',     'page' : '1'})
    listItemAddFolder('Derniers ajouts',        'films.png', {'mode': 'derniersajouts', 'page' : '1'})
    listItemAddFolder('Par auteur',             'films.png', {'mode': 'parauteur',      'page' : '1'})
    listItemAddFolder('Par série',              'films.png', {'mode': 'parserie',       'page' : '1'})
    listItemAddFolder('Par éditeur',            'films.png', {'mode': 'parediteur',     'page' : '1'})
    listItemAddFolder('Par collection',         'films.png', {'mode': 'parcollection',  'page' : '1'})
    listItemAddFolder('Par étiquette',          'films.png', {'mode': 'paretiquette',   'page' : '1'})

    rows = select_sql("SELECT * FROM books")
    for row in rows:
        listItemAddFolder('Actuellement', 'films.png', {'mode': 'actuellement', 'page' : '1'})

elif mode[0] == 'encours':
    listItemAddFolder('Actuellement', 'films.png', {'mode': 'actuellement', 'page' : '1'})

elif mode[0] == 'parauteur':
    rows = select_sql("SELECT id, sort FROM authors ORDER BY sort")
    for row in rows:
        listItemAddFolder(str(row[1]), 'films.png', {'mode': 'auteur', 'id': row[0] ,'page' : '1'})

elif mode[0] == 'auteur':
    id = args['id'][0]
    rows = select_sql(("SELECT * FROM books a, books_authors_link b, authors c WHERE b.book = a.id AND b.author = c.id AND b.author = %s ORDER BY a.sort") % id)
    for row in rows:
        listItemAddBook(row)


elif mode[0] == 'parserie':
    rows = select_sql("SELECT id, sort FROM series ORDER BY sort")
    for row in rows:
        listItemAddFolder(str(row[1]), 'films.png', {'mode': 'serie', 'id': row[0] ,'page' : '1'})

elif mode[0] == 'parediteur':
    rows = select_sql("SELECT id, name FROM publishers ORDER BY name")
    for row in rows:
        listItemAddFolder(str(row[1]), 'films.png', {'mode': 'editeur', 'id': row[0] ,'page' : '1'})


elif mode[0] == 'paretiquette':
    rows = select_sql("SELECT id, name FROM tags ORDER BY name")
    for row in rows:
        listItemAddFolder(str(row[1]), 'films.png', {'mode': 'etiquette', 'id': row[0] ,'page' : '1'})



xbmcplugin.endOfDirectory(addon_handle)