#from tmdbv3api import Account
#from tmdbv3api import Authentication
#from tmdbv3api import TMDb, Movie


from lib.myTMDB import myTMDB
from lib.myTMDB import User

APIKEY = '9c1662a033ca5210dc75b91e0aa9b49e'
LANGUAGE = 'fr-FR'
USERNAME = "doctornono"
PASSWORD = "cousin"
parametresTMDB = {
        "username" 		: USERNAME,
        "password" 		: PASSWORD,
        "api_key"  		: APIKEY,
        "langue" 		: LANGUAGE,
        "token"         : "",
        "session_id" 	: "",
        "user_id"       :"",
        "sql_path" 		: "",
    } 
mytmdb = myTMDB.myTMDB(parametresTMDB)




r = mytmdb.getMovie(17692)
r = mytmdb.getMovie(204)
r = mytmdb.getPeople(6065)

#r = mytmdb.getMovies('popular')
#param = {'idtmdb' : 2034}
#r = mytmdb.getMovies('similar', param)
#r = mytmdb.getSearch('camping')
#r = mytmdb.getList(8173602)


r = mytmdb.userGetAllMoviesWatchlist()
print(str(r))
myuser = User.User()
print(myuser.test())

"""
tmdb = TMDb()

tmdb.api_key = APIKEY
auth = Authentication(username=USERNAME, password=PASSWORD)

account = Account()
details = account.details()

print("You are logged in as %s. Your account ID is %s." % (details.username, details.id))
print("This session expires at: %s" % auth.expires_at)

movie = Movie()

s = movie.search("Gangs of New York")
first_result = s[0]
recommendations = movie.recommendations(first_result.id)

for recommendation in recommendations:
    print("Adding %s (%s) to watchlist." % (recommendation.title, recommendation.release_date))
    #account.add_to_watchlist(details.id, recommendation.id, "movie")


movie = Movie()

recommendations = movie.recommendations(movie_id=111)

for recommendation in recommendations:
    print(recommendation.title)
    print(recommendation.overview)

print('test')
"""