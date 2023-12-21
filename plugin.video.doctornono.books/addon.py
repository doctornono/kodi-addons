import sys
import urllib

import sqlite3
from sqlite3 import Error

import xbmc
import xbmcgui
import xbmcplugin 
import xbmcaddon
import xbmcvfs

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def buildURLIcon(image):
    return my_addon.getAddonInfo('path') + '/resources/icons/' + image


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

    for row in rows:
        print(row)
    
    return rows



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

### ACCUEIL ###
if mode is None:
    rows = select_sql("SELECT * FROM books")
    for row in rows:
        listItemAddFolder('Actuellement', 'films.png', {'mode': 'actuellement', 'page' : '1'})