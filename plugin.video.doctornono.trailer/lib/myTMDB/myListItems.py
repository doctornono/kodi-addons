import xbmc
import xbmcgui
import xbmcplugin 
import xbmcaddon
import xbmcvfs

import urllib

from datetime import datetime, timedelta, date

class myListItems:
    def __init__(self, base_url, my_addon, addon_handle):
        self.BASE_URL = base_url
        self.MY_ADDON = my_addon
        self.ADDON_HANDLE = addon_handle

    def __buildUrl(self, query):
        return self.BASE_URL  + '?' + urllib.parse.urlencode(query)

    def __buildURLIcon(self, image):
        return self.MY_ADDON.getAddonInfo('path') + '/resources/icons/' + image

    def __getTodayOrTomorrow(self, date_str):
        madate = date(int(date_str[0:4]), int( date_str[5:7]), int(date_str[-2:]))
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        if madate == today:
            return "Aujourd'hui"
        elif madate == tomorrow:
            return "Demain"
        else:
            listejours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            listemois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            return "%s %s %s" % (listejours[madate.weekday()], madate.day, listemois[madate.month])

    # PAS BON
    def __getIconResolution(self, filename):
        icon = 'hdr.png'
        if '1080p' in filename: icon='hd-1080.png'
        if '720p' in filename: icon='720p.png'
        if 'UHD' in filename: icon='ultra-hd-4k.png'
        if 'BDRip' in filename: icon='sd.png'
        
        return icon


    def __isInList(self, tmdbid, liste):
        for item in liste:
            if item['tmdb_id'] == int(tmdbid):
                return True
        return False




    def setInfoTagMovie(self, tag, movie, parametres):
        tag.setMediaType('movie')
        tag.setDbId(movie['id'])
        tag.setTitle(movie['title'])
        tag.setSortTitle(movie['title'])
        tag.setOriginalTitle(movie['original_title'])
        #tag.setYear(int(movie['release_date'][0:4]))

        tag.setPlot(movie['overview'])
        tag.setPlotOutline(movie['tagline']) 
        tag.setTagLine(movie['tagline'])
        tag.setDuration(movie['runtime'] * 60 if movie['runtime'] is None else 0)    
        tag.setPremiered(movie['release_date'])        

        tag.setRating(movie['vote_average'], movie['vote_count'], 'tmdb', True)

        tag.setGenres([item['name'] for item in movie['genres']])
        tag.setCountries([item['name'] for item in movie['production_countries']])
        tag.setStudios([item['name'] for item in movie['production_companies']])

        tag.setIMDBNumber(movie['imdb_id'])
        tag.setUniqueIDs({ 'imdb': movie['imdb_id'], 'tmdb' : str(movie['id']) }, "tmdb")

        # imdb top250
        for top in parametres['imdbMoviesTop250']['data']:
            if top['imdb_id'] == movie['imdb_id']:
                tag.setTop250(int(top['rank']))

        # userrating et watched
        for rating in parametres['userMoviesRated']['data']:
            if str(rating['tmdb_id']) == str(movie['id']):
                tag.setUserRating(int(rating['userrating']))
                tag.setPlaycount(1)    

        # certifications
        certification = ''
        for certif in movie['release_dates']['results']:
            if certif['iso_3166_1'] == 'FR':
                for item in certif['release_dates']:
                    if item['type'] == 3:
                        certification = certif['release_dates'][0]['certification']
                        tag.setMpaa('France:' + '-' + str(certification))

        # cast & crew
        credits = movie['credits']
        listCastAndRole = [{'name' : item['name'], 'role' : item['character'], 'thumbnail' : 'https://www.themoviedb.org/t/p/original' + str(item['profile_path']), 'order' :item['order']}  for item in credits['cast'] ]
        
        cast = []
        for actor in listCastAndRole:
            thumbnail = ''
            if 'thumbnail' in actor:
                thumbnail = actor['thumbnail']
            cast.append(xbmc.Actor(actor['name'], actor['role'], actor['order'], thumbnail))        
        tag.setCast(cast)    
        
        listDirector = []
        listWriter = []
        for item in credits['crew']:
            if item['job'] == 'Director':
                listDirector.append(item['name'])
            if item['job'] == 'Writer':
                listWriter.append(item['name'])
        tag.setDirectors(listDirector)        
        tag.setWriters(listWriter)   

        # saga
        if 'belongs_to_collection"' in movie:
            tag.setSet(movie['belongs_to_collection"'][0]['name'])

        # tags
        tag.setTags([item['name'] for item in movie['keywords']['keywords']])

        # trailer par defaut
        for video in movie['videos']['results']:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                tag.setTrailer('plugin://plugin.video.youtube/play/?video_id=' + video['key'])

        # ajouter
        # tag.setSetOverview()
        # tag.setProductionCode()
        # tag.setLastPlayed()
        # tag.setShowLinks()






    def listItemAddMovie(self, tmdbID, data, movie, url = '', isfolder = True, idliste = None, parametres = {}):

        li = xbmcgui.ListItem(data[0]['title'])
        self.setInfoTagMovie(li.getVideoInfoTag(), movie, parametres)
        li.setInfo('video', data[0])
        li.setArt(data[1])

        if isfolder == True:
            url = self.__buildUrl({'mode': 'movie', 'tmdbID' : tmdbID})
        else:
            url = self.__buildUrl({'mode': 'play', 'tmdbID' : tmdbID, 'type':'movie'})

        context = [ 
            ('[B][I]TMDB[/I][/B]',              ''),
            ('Noter ce film',                   'RunPlugin(%s?mode=ratemovie&id=%s)' % (self.BASE_URL, tmdbID)),
            ('Ajouter à une liste',             'RunPlugin(%s?mode=mytmdb-addmovietolist&id=%s)' % (self.BASE_URL, tmdbID)),
            ('Ajouter à une nouvelle liste',    'RunPlugin(%s?mode=mytmdb-addmovietonewlist&id=%s)' % (self.BASE_URL, tmdbID))
        ]

        if idliste is not None:
            context.append(('Retirer de cette liste', 'RunPlugin(%s?mode=mytmdb-removefromlist&id=%s&idliste=%s)' % (self.BASE_URL, tmdbID, idliste)))

        # tester si watchlist
        if self.__isInList(tmdbID, parametres['userMoviesWatchlist']['data']) == False:
            context.append(('Ajouter à la liste de suivi', 'RunPlugin(%s?mode=addtowatchlist&id=%s)' % (self.BASE_URL, tmdbID)))
        else:
            context.append(('Retirer de la liste de suivi', 'RunPlugin(%s?mode=removefromwatchlist&id=%s)' % (self.BASE_URL, tmdbID)))

        #tester si favoris
        if self.__isInList(tmdbID, parametres['userMoviesFavorites']['data']) == False: 
            context.append(('Ajouter à mes favoris', 'RunPlugin(%s?mode=addtofavorites&id=%s)' % (self.BASE_URL, tmdbID)))
        else:
            context.append(('Retirer de mes favoris', 'RunPlugin(%s?mode=removefromfavorites&id=%s)' % (self.BASE_URL, tmdbID)))

        # Trakt
        context.append(('[B][I]TRAKT[/I][/B]',              ''))
        context.append(('Noter ce film',                    'RunPlugin(%s?mode=trakt-ratemovie&id=%s)' % (self.BASE_URL, tmdbID)))
        context.append(('Ajouter à une liste',              'RunPlugin(%s?mode=trakt-addmovietolist&id=%s)' % (self.BASE_URL, tmdbID)))
        context.append(('Ajouter à une nouvelle liste',     'RunPlugin(%s?mode=trakt-addmovietonewlist&id=%s)' % (self.BASE_URL, tmdbID)))
        context.append(('Retirer de cette liste',           'RunPlugin(%s?mode=trakt-removefromlist&id=%s&idliste=%s)' % (self.BASE_URL, tmdbID, idliste)))
        context.append(('Ajouter à la liste de suivi',      'RunPlugin(%s?mode=trakt-addtowatchlist&id=%s)' % (self.BASE_URL, tmdbID)))
        context.append(('Marquer comme vu',                 'RunPlugin(%s?mode=trakt-addtofavorites&id=%s)' % (self.BASE_URL, tmdbID)))
        context.append(('Ajouter à ma collection',          'RunPlugin(%s?mode=trakt-addtorcollection&id=%s)' % (self.BASE_URL, tmdbID)))

        li.addContextMenuItems(context) 
        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True) 







    def setInfoTagTVShow(self, tag, tvshow, parametres):
        tag.setMediaType('tvshow')
        tag.setDbId(tvshow['id'])
        tag.setTitle(tvshow['name'])
        tag.setTvShowTitle(tvshow['name'])
        tag.setSortTitle(tvshow['name'])
        tag.setOriginalTitle(tvshow['original_name'])
        
        #tag.setYear(int(tvshow['first_air_date'][0:4]))
        tag.setTvShowStatus(tvshow['status'])

        tag.setPlot(tvshow['overview'])
        tag.setPlotOutline(tvshow['tagline']) 
        tag.setTagLine(tvshow['tagline'])

        #runtime
       # if tvshow['episode_run_time'] is not []:
      #      tag.setDuration(tvshow['episode_run_time'][0] * 60)

        tag.setPremiered(tvshow['first_air_date'])
        tag.setFirstAired(tvshow['first_air_date'])      

        tag.setRating(tvshow['vote_average'], tvshow['vote_count'], 'tmdb', True)

        tag.setGenres([item['name'] for item in tvshow['genres']])
        tag.setCountries([item['name'] for item in tvshow['production_countries']])
        tag.setStudios([item['name'] for item in tvshow['networks']])

        tag.setIMDBNumber(tvshow['external_ids']['imdb_id'])
        tag.setUniqueIDs({ 'imdb': tvshow['external_ids']['imdb_id'], 'tmdb' : str(tvshow['id']) }, "tmdb")
        
        # imdb top250
        for top in parametres['imdbTVShowsTop250']['data']:
            if top['imdb_id'] == tvshow['external_ids']['imdb_id']:
                tag.setTop250(int(top['rank']))
        
        # userrating et watched
        for rating in parametres['userTVShowRated']['data']:
            if str(rating['tmdb_id']) == str(tvshow['id']):      
                tag.setUserRating(int(rating['userrating']))
                tag.setPlaycount(1)

        # certification
        for certif in tvshow['content_ratings']['results']:
            if certif['iso_3166_1'] == 'FR' and certif['rating'] != 'U':
                tag.setMpaa('France:' + '-' + certif['rating'])
        
        # tags
        tag.setTags([item['name'] for item in tvshow['keywords']['results']])

        # cast & crew
        credits = tvshow['credits']
        listCastAndRole = [{'name' : item['name'], 'role' : item['character'], 'thumbnail' : 'https://www.themoviedb.org/t/p/original' + str(item['profile_path']), 'order' :item['order']}  for item in credits['cast'] ]
        
        cast = []
        for actor in listCastAndRole:
            thumbnail = ''
            if 'thumbnail' in actor:
                thumbnail = actor['thumbnail']
            cast.append(xbmc.Actor(actor['name'], actor['role'], actor['order'], thumbnail))        
        tag.setCast(cast)    
        
        listDirector = []
        for item in tvshow['created_by']:
            listDirector.append(item['name'])
        tag.setDirectors(listDirector)        
        
        
        tag.setTvShowStatus(tvshow['status'])
         
        # ajouter
        # tag.setTrailer()
        # tag.setProductionCode()
        # tag.setLastPlayed()
        # tag.addSeasons()
        # tag.setWriters(listWriter)      




    def listItemAddTVShow(self, tmdbID, data, tvshow, url = '', isfolder = True, idliste = None, parametres = {}):

        li = xbmcgui.ListItem(data[0]['title'])
        self.setInfoTagTVShow(li.getVideoInfoTag(), tvshow, parametres)        
        li.setInfo('video', data[0])
        li.setArt(data[1])
        xbmc.log(str(tvshow))

        if isfolder == True:
            url = self.__buildUrl({'mode': 'tvshow', 'tmdbID' : tmdbID})
        else:
            url = self.__buildUrl({'mode': 'play', 'id' : tmdbID, 'type':'tvshow'})
        
        context = [ 
            ('Noter cette série', 'RunPlugin(%s?mode=ratetvshow&id=%s)' % (self.BASE_URL, tmdbID)),
            ('Ajouter à une liste', 'RunPlugin(%s?mode=addtvshowtolist&id=%s)' % (self.BASE_URL, tmdbID)),
            ('Ajouter à une nouvelle liste', 'RunPlugin(%s?mode=addtvshowtonewlist&id=%s)' % (self.BASE_URL, tmdbID))
        ]

        if idliste is not None:
            context.append(('Retirer de cette liste', 'RunPlugin(%s?mode=removetvshowfromlist&id=%s&idliste=%s)' % (self.BASE_URL, tmdbID, idliste)))

        # tester si watchlist
        if self.__isInList(tmdbID, parametres['userTVShowWatchlist']['data']) == False:
            context.append(('Ajouter à la liste de suivi', 'RunPlugin(%s?mode=addtvshowtowatchlist&id=%s)' % (self.BASE_URL, tmdbID)))
        else:
            context.append(('Retirer de la liste de suivi', 'RunPlugin(%s?mode=removetvshowfromwatchlist&id=%s)' % (self.BASE_URL, tmdbID)))

        #tester si favoris
        if self.__isInList(tmdbID, parametres['userTVShowFavorites']['data']) == False:  
            context.append(('Ajouter à mes favoris', 'RunPlugin(%s?mode=addtvshowtofavorites&id=%s)' % (self.BASE_URL, tmdbID)))
        else:
            context.append(('Retirer de mes favoris', 'RunPlugin(%s?mode=removetvshowfromfavorites&id=%s)' % (self.BASE_URL, tmdbID)))


        li.addContextMenuItems(context)
        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True) 





    def listItemAddSeasons(self, tmdbID, data, tvshow):

        if 'fanarttv' in data:
            fanarttv =  data['fanarttv']
        else:
            fanarttv = []

        for saison in data['seasons']:
            li = xbmcgui.ListItem(saison['name'])
            tvshow[0]['media_type'] = 'season'
            tvshow[0]['year'] = saison['air_date']
            tvshow[0]['premiered'] = saison['air_date']
            tvshow[0]['plot'] = saison['overview']
            tvshow[0]['saison'] = saison['season_number']
            tvshow[0]['episode'] = saison['episode_count']

            li.setInfo('video', tvshow[0])

            poster = ''
            if 'seasonposter' in fanarttv:
                for item in fanarttv['seasonposter']:
                    if item['lang'] == 'fr' and int(item['season']) == int(saison['season_number']):
                        poster = item['url']
                if poster == '':
                    for item in fanarttv['seasonposter']:
                        if item['lang'] == 'en' and int(item['season']) == int(saison['season_number']):
                            poster = item['url']

            banner = ''
            if 'seasonbanner' in fanarttv:
                for item in fanarttv['seasonbanner']:
                    if item['lang'] == 'fr' and int(item['season']) == int(saison['season_number']):
                        banner = item['url']
                if banner == '':
                    for item in fanarttv['seasonbanner']:
                        if item['lang'] == 'en' and int(item['season']) == int(saison['season_number']):
                            banner = item['url']

            fanart = ''
            if 'seasonthumb' in fanarttv:
                for item in fanarttv['seasonthumb']:
                    if item['lang'] == 'fr' and int(item['season']) == int(saison['season_number']):
                        fanart = item['url']
                if fanart == '':
                    for item in fanarttv['seasonthumb']:
                        if item['lang'] == 'en' and item['season'] == saison['season_number']:
                            fanart = item['url']

            art = {    
                #    'thumb'     :  poster, #'https://image.tmdb.org/t/p/w185' + poster_path, 
                        'poster'    :  poster,
                        'fanart'    :  fanart,
                        'banner'    : banner,
                #      'clearart'  : clearart, #'https://images.fanart.tv/fanart/the-northman-62444bfab1c9c.png',
                #     'clearlogo' : clearlogo #'https://images.fanart.tv/fanart/the-northman-61ec51afd4b0c.png',
                    # 'landscape' : 'https://images.fanart.tv/fanart/the-northman-62449fb348127.jpg',
                    #  'icon'      : poster #buildURLIcon('star.png') #'https://library.kissclipart.com/20180831/rfw/kissclipart-film-vector-png-clipart-hollywood-clip-art-aa8d3c1c62df7f9e.pngs'
            }         
            li.setArt(art)
            li.setCast(tvshow[2])
            li.setRating("tmdb", tvshow[0]['rating'], tvshow[0]['votes'], False)
            li.setLabel('%s  (0/%s)' % (saison['name'], str(saison['episode_count'])))
            url = url = self.__buildUrl({'mode': 'episodes', 'tmdbID' : tmdbID, 'season_number' : saison['season_number']}) 

            li.setProperty('isplayable','false')

            xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)     


    def listItemAddEpisode(self, tmdbid, episode, infos):
        li = xbmcgui.ListItem(episode['name'])
        li.setProperty('isplayable','true')
        li.setInfo('video', infos[0])
        url = url = self.__buildUrl({'mode': 'playepisode', 'tmdbID' : tmdbid}) 
        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = False)                 


    def listItemAddSeason(self, tmdbID, episode, infos):
        li = xbmcgui.ListItem(episode['name'])
        li.setProperty('isplayable','true')
        #infos = listItemSetInfoEpisode(tmdbID, tvshow, season , episode)
        infos[0]['media_type'] = 'episode'
        li.setInfo('video', infos[0])
        li.setCast(infos[2])
        li.setArt(infos[1])
        url = url = self.__buildUrl({'mode': 'playepisode', 'tmdbID' : tmdbID}) 
        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = False) 








    def listItemAddFile(self, tmdbID, file, data):

        li = xbmcgui.ListItem(file['file_name'])
        #li.setInfo('video', data[0])

        data[1]['thumb']= self.buildURLIcon(self.__getIconResolution(file['file_name'])) 
        li.setArt(data[1])
        
        li.setCast(data[2])
        li.setUniqueIDs({ 'imdb': data[0]['imdbnumber'], 'tmdb' : data[0]['code'] }, "tmdb")
        li.setRating("imdb", 4.6, 8940, True)
        li.setRating("tmdb", 8.6, 898840, False)

        size = round(file['file_size'] / 1000000000, 2)
        li.setLabel(str(size) + 'Go - ' + file['file_name'])
        
        code = file['file_code']
        #url = 'plugin://plugin.video.vstream/?site=cHosterGui&function=play&title=Voici+votre+lien%3A++&sCat=5&sMediaUrl=https%3A%2F%2Fuptostream.com%2F' + code + '&sHosterIdentifier=uptostream&sFileName=Voici+votre+lien%3A+&sTitleWatched=voicivotrelien&sTitle=Voici+votre+lien%3A++&sId=cHosterGui&siteUrl=http%3A%2F%2Fvenom&sourceName=cHome&sourceFav=showHostDirect'
        url = 'plugin://plugin.video.vstream/?site=cHosterGui&function=play&title=Voici+votre+lien%3A++&sCat=5&sMediaUrl=https%3A%2F%2Fuptobox.com%2F' + code + '&sHosterIdentifier=uptobox&sFileName=Voici+votre+lien%3A+&sTitleWatched=voicivotrelien&sTitle=Voici+votre+lien%3A++&sId=cHosterGui&siteUrl=http%3A%2F%2Fvenom&sourceName=cHome&sourceFav=showHostDirect'

        li.setProperty('isplayable','true')

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = False) 



    def listItemAddFolder(self, label, icon, url, context = None, infos = None, pictures = None, isfolder = True, isPlayable = True):
        
        li = xbmcgui.ListItem(label)
        url = self.__buildUrl(url)
        if isfolder == False:
            if isPlayable == True:
                li.setProperty('isplayable','true')
            else:
                li.setProperty('isplayable','false')

        if pictures != None:
            li.setArt(pictures)
        else:
            li.setArt({'thumb' : self.__buildURLIcon(icon)})
            
        li.setInfo('video', infos)
        if context != None:
            li.addContextMenuItems(context) 

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = isfolder)


    def listItemAddList(self, list):

        url = self.__buildUrl({'mode': 'mytmdb-list', 'tmdbid' : list['id']})
        li = xbmcgui.ListItem(list['name'])
        li.setInfo('video', { 'genre': list['description']  + ' (' + str(list['item_count'])  + ' films)'})
        if list['poster_path'] is None:
            li.setArt({'thumb' :  self.__buildURLIcon('list.png')})
        else:
            li.setArt({ 'thumb': 'https://image.tmdb.org/t/p/w500' + list['poster_path'], 'poster' : 'https://image.tmdb.org/t/p/w500' + list['poster_path'], 'fanart' : 'https://image.tmdb.org/t/p/original' + list['poster_path'] })
        li.addContextMenuItems([('Supprimer cette liste', 'RunPlugin(%s?mode=mytmdb-deletelist&id=%s)' % (self.BASE_URL, list['id']))])  

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)      



    def listItemAddTraktList(self, list):

        url = self.__buildUrl({'mode': 'trakt-list', 'traktid' : list['ids']['trakt']})
        li = xbmcgui.ListItem(list['name'])
        li.setInfo('video', { 'genre': list['description']  + ' (' + str(list['item_count'])  + ' films)'})
        
        li.setArt({'thumb' :  self.__buildURLIcon('list.png')})
        li.addContextMenuItems([('Supprimer cette liste', 'RunPlugin(%s?mode=trakt-deletelist&id=%s)' % (self.__buildUrl, list['ids']['trakt']))])  

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)      



    def listItemAddTraktLikedList(self, list):

        url = self.__buildUrl({'mode': 'trakt-list', 'traktid' : list['list']['ids']['trakt']})
        li = xbmcgui.ListItem(list['list']['name'])
        li.setInfo('video', { 'genre': list['list']['description']  + ' (' + str(list['list']['item_count'])  + ' films)'})
        
        li.setArt({'thumb' :  self.__buildURLIcon('list.png')})
        li.addContextMenuItems([('Supprimer cette liste', 'RunPlugin(%s?mode=trakt-deletelike&id=%s)' % (self.__buildUrl, list['list']['ids']['trakt']))])  

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)      





    def listItemAddTrailer(self, infos, trailer):

        if trailer['site']=='YouTube' and (trailer['type'] == 'Trailer' or trailer['type']== 'Teaser'):
            url = 'plugin://plugin.video.youtube/play/?video_id=' + trailer['key']
            nom = trailer['name']
            li = xbmcgui.ListItem(nom)
            li.setArt({ 'thumb': self.__buildURLIcon(trailer['iso_3166_1']+'.png'), 'poster' : 'https://image.tmdb.org/t/p/w500' + infos['poster_path'], 'fanart' : 'https://image.tmdb.org/t/p/original' + infos['backdrop_path'] })
            li.setInfo('video', { 'genre': trailer['type'] + ' - ' + str(trailer['size']) })

            xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = False)    



    def listItemAddCast(self, infos, cast):

        if cast['profile_path'] is None:
            thumb = self.__buildURLIcon('cast.png')
            poster = self.__buildURLIcon('cast.png')
        else:
            thumb = 'https://image.tmdb.org/t/p/w500' + cast['profile_path']
            poster = 'https://image.tmdb.org/t/p/w500' + cast['profile_path']
        #fanart = 'https://image.tmdb.org/t/p/original' + infos['backdrop_path'] if infos['backdrop_path'] is None else fanart = ''
            
        url = self.__buildUrl({'mode': 'actor', 'tmdbid' : cast['id']})
        li = xbmcgui.ListItem(cast['name'])
        li.setArt({ 'thumb': thumb, 'poster' : poster, 'fanart' : 'https://image.tmdb.org/t/p/original' + infos['backdrop_path'] if infos['backdrop_path'] is None else  '' })
        if cast['known_for_department'] == "Acting":
            li.setInfo('video', { 'genre': cast['character']  })
        elif cast['known_for_department'] == "Directing":
            li.setInfo('video', { 'genre': cast['job']  })

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)   


    def listItemAddSaga(self, list):

        url = self.__buildUrl({'mode': 'saga', 'tmdbid' : list['id']})
        li = xbmcgui.ListItem(list['name'])
        if list['poster_path'] is None:
            li.setArt({'thumb' :  self.__buildURLIcon('movie.png')})
        else:
            li.setArt({ 'thumb': 'https://image.tmdb.org/t/p/w500' + list['poster_path'], 'poster' : 'https://image.tmdb.org/t/p/w500' + list['poster_path'], 'fanart' : 'https://image.tmdb.org/t/p/original' + list['backdrop_path'] })

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)      


    def listItemAddStudio(self, list):

        url = self.__buildUrl({'mode': 'studio', 'tmdbid' : list['id']})
        li = xbmcgui.ListItem(list['name'])
        if list['logo_path'] is None:
            li.setArt({'thumb' :  self.__buildURLIcon('studio.png')})
        else:
            li.setArt({ 'thumb': 'https://image.tmdb.org/t/p/w500' + list['logo_path'], 'poster' : 'https://image.tmdb.org/t/p/w500' + list['logo_path'], 'fanart' : 'https://image.tmdb.org/t/p/original' + list['logo_path'] })

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)   


    def listItemAddTag(self, list):

        url = self.__buildUrl({'mode': 'tag', 'tmdbid' : list['id']})
        li = xbmcgui.ListItem(list['name'])
        li.setArt({ 'thumb': 'tag.png'})
        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)   



    def listItemAddTraktFriend(self, list):

        url = self.__buildUrl({'mode': 'trakt-menu', 'trakt-user' : list['user']['ids']['slug']})
        li = xbmcgui.ListItem(list['user']['name'])
            
        li.setArt({'thumb' :  self.__buildURLIcon('list.png')})

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)      


    # ListItem de séparation non cliquable, sans infos, ...
    def listItemAddSeparator(self, type, texte):
        if type == 'date':
            texte = self.__getTodayOrTomorrow(texte)
            icone = 'upcoming.png'
        elif type == 'search':
            icone = 'search.png'

        url = self.__buildUrl({'mode': 'nothing'})
        li = xbmcgui.ListItem(texte)
        li.setArt({'thumb' :  self.__buildURLIcon(icone)})
        li.setProperty('isplayable','false')
        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = False)      


    def listItemAddPerson(self, cast):

        if cast['profile_path'] is None:
            thumb = self.__buildURLIcon('cast.png')
            poster = self.__buildURLIcon('cast.png')
        else:
            thumb = 'https://image.tmdb.org/t/p/w500' + cast['profile_path']
            poster = 'https://image.tmdb.org/t/p/w500' + cast['profile_path']
            
        url = self.__buildUrl({'mode': 'actor', 'tmdbid' : cast['id']})
        li = xbmcgui.ListItem(cast['name'])
        li.setArt({ 'thumb': thumb, 'poster' : poster })

        xbmcplugin.addDirectoryItem(handle=self.ADDON_HANDLE, url=url, listitem=li, isFolder = True)   