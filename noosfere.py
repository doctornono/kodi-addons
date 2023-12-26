from bs4 import BeautifulSoup
import urllib
from urllib import request

import re
import scraperNoosfere

url = 'https://www.noosfere.org/livres/collection.asp?numcollection=1975551973'
req = urllib.request.urlopen(url)
response = req.read()
req.close()
soup = BeautifulSoup(response, 'html.parser')
#print(soup)
tableau = soup.find('table', class_="noocadre_pad5")
table = tableau.find_next('table')
lignes = table.find_all('tr')
for ligne in lignes:
    #print(ligne, '++++++++++++++++++')
    numero =  str(ligne.find('td').get_text())
    lien = ligne.find_all('a')
    titre = lien[0].get_text()
    fiche = lien[0]['href']
    # Extraction du ISBN
    match = re.search(r'./EditionsLivre\.asp\?numitem=(\d+)', str(ligne))
    numitem = match.group(1).strip() if match else None
     
    print(numero,  titre,  numitem)
    """
    url = 'https://www.noosfere.org/livres/EditionsLivre.asp?numitem=' + numitem
    req = urllib.request.urlopen(url)
    response = req.read()
    req.close()
    soupbook = BeautifulSoup(response, 'html.parser')
    title = soupbook.title.get_text()
    print(str(title))
    """
myscrap = scraperNoosfere
print(str(myscrap.scraperNoosfere.scrapLivre(456)))