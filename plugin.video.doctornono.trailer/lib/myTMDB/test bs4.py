from bs4 import BeautifulSoup
from urllib import request

url = 'http://www.fortwiki.com/Battery_Adair'
req = request.Request(url)
r = request.urlopen(req)
soup = BeautifulSoup(r, "html.parser")
print(soup)
b = soup.find('b', text='Maps & Images')
if b:
    lat_long = b.find_next().text