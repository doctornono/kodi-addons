from bs4 import BeautifulSoup
import urllib
from urllib import request

import re

url = 'https://www.noosfere.org/livres/collection.asp?numcollection=1975551973'
req = urllib.request.urlopen(url)
response = req.read()
req.close()
soup = BeautifulSoup(response, 'html.parser')
#print(soup)
tableau = soup.find_all('table', class_="noocadre_pad5")[0]
lignes = tableau.find_all('tr')
for ligne in lignes:
    #print(ligne, '++++++++++++++++++')
    numero =  str(ligne.find('td').get_text())
    lien = ligne.find_all('a')
    titre = lien[0].get_text()
    fiche = lien[0]['href']

    #print(titre, numero)
    expression_reguliere = r'numitem=(\d+)'

    # Recherche de la correspondance dans le fiche
    correspondance = re.search(expression_reguliere, fiche)

    # Vérification de la correspondance et extraction de la valeur de numitem
    if correspondance:
        valeur_numitem = correspondance.group(1)
        #print("La valeur de numitem est :", valeur_numitem)
    else:
       # print("Aucune correspondance trouvée.")
        valeur_numitem = None

    url = 'https://www.noosfere.org/livres/' + fiche.replace('./', '')
    req = urllib.request.urlopen(url)
    response = req.read()
    req.close()
    soupbook = BeautifulSoup(response, 'html.parser')
    title = soupbook.title.get_text()
    #print(title)
    if  title.find('Fiche livre'):
        #print(title)
        dd = soupbook.find_all('td', class_="vousetesici")
        #ddd = dd.find_all('a')
        #print(str(dd))
        expression_reguliere = r'choix\.asp\?numlivre=(\d+)'

        # Recherche de la correspondance dans le fiche
        correspondance = re.search(expression_reguliere, str(dd))

        # Vérification de la correspondance et extraction de la valeur de numitem
        if correspondance:
            valeur_numlivre = correspondance.group(1)
           # print("La valeur de numlivre est :", valeur_numlivre)
        else:
            #print("Aucune correspondance trouvée.")
            valeur_numlivre =None
        couv = soupbook.find_all('div', id="quatrieme")
        print(titre, numero, valeur_numitem, valeur_numlivre)
        print('-----------------')
        print(couv)