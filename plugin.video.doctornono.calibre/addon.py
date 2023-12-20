import sys
import urllib
from urllib.parse import urlparse
from urllib import request

import re
import os

import xbmc
import xbmcgui
import xbmcplugin 
import xbmcaddon

from bs4 import BeautifulSoup, Tag, NavigableString
from random import *

import sqlite3
from sqlite3 import Error

import webbrowser

import requests
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

mode = args.get('mode', None)

xbmcplugin.setContent(addon_handle, 'movies')

my_addon = xbmcaddon.Addon('plugin.video.doctornono.calibre')
profile = xbmc.translatePath( my_addon.getAddonInfo('profile'))


def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)


def buildURLIcon(database, chemin):
    url =database  + chemin + "/cover.jpg"
    return url.replace('\\', '/')
 

def buildFolderIcon(image):
    return my_addon.getAddonInfo('path') + 'resources\\icons\\' + image


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
        conn = sqlite3.connect(db_file, timeout=10)
    except Error as e:
        print(e)

    return conn



def select_books(database, selection, id = ''):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    bd = database.replace('smb:', '') + 'metadata.db'
    print ('ddddddddddddddddddddddddddd',bd)
    conn = create_connection(bd)
    cur = conn.cursor()

    if selection == 'all' :
        sql = "SELECT a.id, a.title, a.sort, a.pubdate, a.author_sort, a.path, b.text, c.name, e.format, e.name FROM books a, comments b, publishers c, books_publishers_link d, data e WHERE a.id = b.book AND d.book = a.id AND d.publisher = c.id AND a.id = e.book"
    elif selection == 'authors':
        sql = "SELECT id, sort, link FROM authors ORDER BY sort"
    elif selection == 'series':
        sql = "SELECT id, name FROM series ORDER BY name"        
    elif selection == 'editors':
        sql = "SELECT id, name FROM publishers ORDER BY name" 
    elif selection == 'tags':
        sql = "SELECT id, name FROM tags ORDER BY name" 
    elif selection == 'listeauthors':
        sql = "SELECT a.id, a.title, a.sort, a.pubdate, a.author_sort, a.path, b.text, c.name, e.format, e.name FROM books a, comments b, publishers c, books_publishers_link d, data e, books_authors_link f WHERE a.id = b.book AND d.book = a.id AND d.publisher = c.id AND a.id = e.book AND a.id = f.book AND f.author = " + id
    elif selection == 'listeseries':
        sql = "SELECT a.id, a.title, a.sort, a.pubdate, a.author_sort, a.path, b.text, c.name, e.format, e.name FROM books a, comments b, publishers c, books_publishers_link d, data e, books_series_link f WHERE a.id = b.book AND d.book = a.id AND d.publisher = c.id AND a.id = e.book AND a.id = f.book AND f.series = " + id
    elif selection == 'listetags':
        sql = "SELECT a.id, a.title, a.sort, a.pubdate, a.author_sort, a.path, b.text, c.name, e.format, e.name FROM books a, comments b, publishers c, books_publishers_link d, data e, books_tags_link f WHERE a.id = b.book AND d.book = a.id AND d.publisher = c.id AND a.id = e.book AND a.id = f.book AND f.tag = " + id
    elif selection == 'listeeditors':
        sql = "SELECT a.id, a.title, a.sort, a.pubdate, a.author_sort, a.path, b.text, c.name, e.format, e.name FROM books a, comments b, publishers c, books_publishers_link d, data e WHERE a.id = b.book AND d.book = a.id AND a.id = e.book AND d.publisher = c.id AND d.publisher = " + id
    elif selection == 'lastbooks' :
        sql = "SELECT a.id, a.title, a.sort, a.pubdate, a.author_sort, a.path, b.text, c.name, e.format, e.name FROM books a, comments b, publishers c, books_publishers_link d, data e WHERE a.id = b.book AND d.book = a.id AND d.publisher = c.id AND a.id = e.book ORDER BY timestamp DESC LIMIT 100"


    cur.execute(sql)
    print(sql)
    rows = cur.fetchall()
    return rows




def listAddFolder(label, icon, url, isFolder = True , context = None):
    
    li = xbmcgui.ListItem(label)
    url = build_url(url)
    li.setProperty('isplayable','false')
    li.setArt({'thumb' : buildFolderIcon(icon)})
    if context != None:
        li.addContextMenuItems(context) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = isFolder)  


    


def listAddBook(label, icon, url, context = None, infos = None, database = None):
    
    li = xbmcgui.ListItem(label)
    url = build_url(url)
    li.setProperty('isplayable','false')
    li.setArt({'thumb' : buildURLIcon(database, icon), 'poster' : buildURLIcon(database, icon), 'fanart' : buildURLIcon(database, icon)})
    li.setInfo('video', infos)
    if context != None:
        li.addContextMenuItems(context) 

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = False)    


def listAddButton(label, icon, url, context = None, infos = None):
    
    li = xbmcgui.ListItem(label)

    url = build_url(url)
    li.setProperty('isplayable','false')
    li.setArt({'thumb' : buildFolderIcon(icon)})
    #li.setInfo('video', infos)
    if context != None:
        li.addContextMenuItems(context) 

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder = False)    



def listItemSetInfo(book):
    infos = {    
            'title': book[1], 
            'genre' : book[7],
            'year' : book[3],
            'rating' : book[8],
            'plot' : cleanhtml(book[6]),
            'director' : book[4],
            'code' : book[0],           
            'mediatype' : 'movie'
    } 
    return infos







def biblioExistXML():
    if os.path.isfile(profile+'biblio.xml') == False:
        f = open(profile+'biblio.xml', "w")
        f.write("<bibliotheques></bibliotheques>")
        f.close()  


def biblioOpenXML():
    lienimdb = 'file:' + urllib.request.pathname2url(profile + 'biblio.xml')
    req =  urllib.request.urlopen(lienimdb)
    response = req.read()
    req.close()
    return response


def biblioSaveXML(chaine):
    f = open(profile+'biblio.xml', "w")
    f.write(chaine)
    f.close()


def biblioAdd(name, chemin):
    soup = BeautifulSoup(biblioOpenXML(), 'html.parser')
    tag = soup.new_tag('bibliotheque')
    tag['id']= randint(1,1000000)
    tag['name'] = name
    tag['chemin'] = chemin
    soup.bibliotheques.append(tag)
    biblioSaveXML(soup.prettify())


def biblioDelete(id):
    soup = BeautifulSoup(biblioOpenXML(), 'html.parser')
    for liste in soup.find_all('bibliotheque'):
        if liste['id']== str(id):
             # supprimer le noeud
            liste.extract()

    biblioSaveXML(soup.prettify())


def biblioRename(id, new):
    soup = BeautifulSoup(biblioOpenXML(), 'html.parser')
    for liste in soup.find_all('bibliotheque'):
        if liste['id']== str(id):
            liste['name']= new

    biblioSaveXML(soup.prettify())



def biblioIcon(page):
    if page == 'authors':
        return 'auteur.png'
    elif page == 'editors':
        return 'publisher.png'
    elif page == 'series':
        return 'serie.png'
    elif page == 'tags':
        return 'tags.png'



biblioExistXML()

print('ossssssssssssssssssssssssssss', os.name)

#home
if mode is None:
    soup = BeautifulSoup(biblioOpenXML(), 'html.parser')
    for link in soup.findAll('bibliotheque'):
        listAddFolder(link['name'], 'biblio.png', {'mode': 'biblio', 'page' : link['id'], 'chemin' : link['chemin']}, True, [ ('Supprimer la bibliothèque', 'RunPlugin(%s?mode=deletebiblio&id=%s)' % (base_url, link['id'])),  ('Renommer la bibliothèque', 'RunPlugin(%s?mode=renamebiblio&id=%s)' % (base_url, link['id'])) ]) 

    listAddButton('Ajouter une bibliothèque', 'add.png', {'mode': 'addbiblio', 'page' : '1'})
    headers = {"User-Agent": "df"}
    response = requests.get("http://4ce5e2d62ee2c10e43c709f9b87c44d5.streamhost.cc/m3u8/France/28d64aa3c40ce6b.m3u8", headers=headers)
    print(response)

elif mode[0] == 'biblio':
    database = args['chemin'][0]
    listAddFolder('Tous les livres', 'biblio.png', {'mode': 'liste', 'page' : 'all', 'id': 'all', 'chemin' : database})
    listAddFolder('Par auteur', 'auteur.png', {'mode': 'folder', 'page' : 'authors', 'chemin' : database})
    listAddFolder('Par série', 'serie.png', {'mode': 'folder', 'page' : 'series', 'chemin' : database})
    listAddFolder('Par éditeur', 'publisher.png', {'mode': 'folder', 'page' : 'editors', 'chemin' : database})
    listAddFolder('Par étiquette', 'tags.png', {'mode': 'folder', 'page' : 'tags', 'chemin' : database})
    listAddFolder('Derniers ajouts', 'last.png', {'mode': 'liste', 'page' : 'lastbooks', 'id': 'lastbooks', 'chemin' : database})


elif mode[0] == 'folder':
    page = args['page'][0]
    database = args['chemin'][0]
    rows = select_books(database, page)
    for row in rows:
        id = row[0]
        label = row[1]

        listAddFolder(label, biblioIcon(page), {'mode': 'liste', 'page' : 'liste'+page, 'id': id, 'chemin' : database})  


elif mode[0] == 'liste':
    page = args['page'][0]
    id = args['id'][0]
    database = args['chemin'][0]
    rows = select_books(database, page, id)
    for row in rows:
        infos = listItemSetInfo(row)
        url = database.replace('/', '\\') + row[5].replace('/', '\\') + '\\' + row[9] + '.' + row[8]
        url = url.replace('smb:', '')
        listAddBook(str(row[1]), row[5], {'mode': 'player', 'chemin' : url},  None, infos, database )


elif mode[0] == 'addbiblio':
    dialog = xbmcgui.Dialog()
    name = dialog.input('Saisissez un nom', type=xbmcgui.INPUT_ALPHANUM)
    folder = dialog.browse(0, 'Kodi', 'files', '', False, False, 'False', False)
    biblioAdd(name, folder)
    xbmc.executebuiltin('Container.Refresh')


elif mode[0] == 'deletebiblio':
    id = args['id'][0]
    biblioDelete(id)
    xbmc.executebuiltin('Container.Refresh')


elif mode[0] == 'renamebiblio':
    id = args['id'][0]
    dialog = xbmcgui.Dialog()
    new = dialog.input('New list name', defaultt='', type=xbmcgui.INPUT_ALPHANUM)    
    biblioRename(id, new)
    xbmc.executebuiltin('Container.Refresh')

elif mode[0] == 'player':
    chemin = args['chemin'][0]
    webbrowser.open(chemin)
    

        

xbmcplugin.endOfDirectory(addon_handle)