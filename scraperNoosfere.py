from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import json

import re

class scraperNoosfere:
    def scrapCollection(collection_id):
        url = 'https://www.noosfere.org/livres/collection.asp?numcollection=' + collection_id
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req)
        resultat = []
            # Vérification de la réussite de la requête
        if response.getcode() == 200:
            soup = BeautifulSoup(response.read(), 'html.parser')
            #print(soup)
            tableau = soup.find('table', class_="noocadre_pad5")
            table = tableau.find_next('table')
            lignes = table.find_all('tr')
            for ligne in lignes:
                json = {}
                #print(ligne, '++++++++++++++++++')
                numero =  str(ligne.find('td').get_text())
                lien = ligne.find_all('a')
                titre = lien[0].get_text()
                fiche = lien[0]['href']
                # Extraction du ISBN
                match = re.search(r'./EditionsLivre\.asp\?numitem=(\d+)', str(ligne))
                numitem = match.group(1).strip() if match else None
                
                #print(numero,  titre,  numitem)
                json['numero'] = str(ligne.find('td').get_text().strip())
                json['titre'] = lien[0].get_text()
                json['numitem'] = numitem
                resultat.append(json)
            

            for item in resultat:
                print(item['numitem'])


                
            return resultat 


    def scrapLivre(numlivre, html = None):
        if html == None:
            url = "https://www.noosfere.org/livres/niourf.asp?numlivre=" + numlivre

            # Envoi de la requête HTTP
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req)

            # Vérification de la réussite de la requête
            if response.getcode() == 200:
                # Analyse du contenu de la page avec BeautifulSoup et le parseur html.parser
                html = response.read()



            soup = BeautifulSoup(html, 'html.parser')

            # Extraction des informations
            titre = soup.find('span', {'class': 'TitreNiourf'}).text.strip()
            auteur = soup.find('span', {'class': 'AuteurNiourf'}).text.strip()

            fiche = str(soup.find('span', {'class': 'ficheNiourf'}))
            ficheauteur = str(soup.find('span', {'class': 'AuteurNiourf'}))

            # Extraction du titre original
            match = re.search(r'Titre original\s*:\s*<i>([^,]+)', fiche, re.IGNORECASE)
            titreoriginal = match.group(1).strip() if match else None

            # Extraction de l'année originale
            match = re.search(r'Titre original\s*:\s*<i>[^,]+,\s*(.*?)</i>', fiche, re.IGNORECASE)
            anneeoriginale = match.group(1).strip() if match else None    

            # Extraction de l'illustrateur
            match = re.search(r'Illustration de\s+<a[^>]+>(.*?)</a>', fiche, re.DOTALL)
            illustration = match.group(1).strip() if match else None    

            # Extraction de l'illustrateur
            match = re.search(r'Traduction de\s+<a[^>]+>(.*?)</a>', fiche, re.DOTALL)
            traduction = match.group(1).strip() if match else None    

            # Extraction du cycle
            match = re.search(r'Cycle : <a[^>]+>(.*?)</a>', fiche, re.DOTALL)
            serie = match.group(1).strip() if match else None

            # Extraction du tome
            match = re.search(r'vol\.\s+(\d+)', fiche)
            tome = match.group(1).strip() if match else None

            # Extraction de l'éditeur
            match = re.search(r'<a href="editeur.asp[^>]+>(.*?)</a>', fiche, re.DOTALL)
            editeur = match.group(1).strip() if match else None

            # Extraction de la collection
            match = re.search(r'coll\.\s+<a[^>]+>(.*?)</a>', fiche, re.DOTALL)
            collection = match.group(1).strip() if match else None

            # Extraction du numéro de collection
            match = re.search(r'n°\s+(\d+)', fiche)
            id = match.group(1).strip() if match else None

            sousfiche = str(soup.find('span', {'class': 'sousFicheNiourf'}))
            
            # Extraction du depot legal
            match = re.search(r'Dépôt légal : <a[^>]+>(.*?)</a>', sousfiche)
            depotlegal = match.group(1).strip() if match else None
            
            # Extraction du nombre de pages
            match = re.search(r'(\d+) pages', sousfiche, re.DOTALL)
            pages = match.group(1).strip() if match else None

            # Extraction du ISBN
            match = re.search(r'ISBN : (\S+)', sousfiche)
            isbn = match.group(1).strip() if match else None
            
            # Extraction du genre
            match = re.search(r'Genre : (.*?)<br/>', sousfiche, re.DOTALL)
            genre = match.group(1).strip() if match else None

            # Extraction de l'edition
            match = re.search(r'Réédition', sousfiche, re.DOTALL)
            if match:
                edition = 'Réédition'
            match = re.search(r'Première édition', sousfiche, re.DOTALL)
            if match:
                edition = 'Première édition'    

            # Extraction de la categorie comme Roman, ...
        
            match = re.search(r'Roman', sousfiche, re.DOTALL)
            if match:
                categorie = 'Roman'
            match = re.search(r'Recueil de nouvelles', sousfiche, re.DOTALL)
            if match:
                categorie = 'Recueil de nouvelles'        
            match = re.search(r'Recueil de romans', sousfiche, re.DOTALL)
            if match:
                categorie = 'Recueil de romans'  
            match = re.search(r'Anthologie', sousfiche, re.DOTALL)
            if match:
                categorie = 'Anthologie'  
            match = re.search(r'Biographie', sousfiche, re.DOTALL)
            if match:
                categorie = 'Biographie'
            match = re.search(r'Revue', sousfiche, re.DOTALL)
            if match:
                categorie = 'Revue'        
            match = re.search(r'Novella', sousfiche, re.DOTALL)
            if match:
                categorie = 'Novella'  


            quatrieme = str(soup.find('div', {'id': 'quatrieme'}))

            urlcouv = soup.find('img', {'name': 'couverture'})['src']




            # ******** ID NOOSFERE ********
            match = re.search(r'<a[^>]+href="/livres/auteur.asp\?NumAuteur=(-?\d+)".*?>(.*?)</a>' , ficheauteur, re.DOTALL)
            id_auteur = match.group(1).strip() if match else None

            match = re.search(r'https://www.noosfere.org/livres/niourf.asp\?numlivre=(\d+)', url, re.DOTALL)
            id_livre = match.group(1).strip() if match else None

            match = re.search(r'<a[^>]+href="editeur.asp\?numediteur=(\d+)"[^>]*>(.*?)</a>', fiche, re.DOTALL)
            id_editeur = match.group(1).strip() if match else None

            match = re.search(r'<a[^>]+href="collection.asp\?NumCollection=(-?\d+)&amp;numediteur=\d+"[^>]*>(.*?)</a>', fiche, re.DOTALL)
            id_collection = match.group(1).strip() if match else None

            match = re.search(r'Cycle\s*:\s*<a[^>]+serie.asp\?numserie=(\d+)[^>]*>(.*?)</a>', fiche, re.DOTALL)
            id_serie = match.group(1).strip() if match else None

            match = re.search(r'Illustration de\s*<a[^>]+auteur.asp\?NumAuteur=(\d+)[^>]*>(.*?)</a>', fiche, re.DOTALL)
            id_illustrateur = match.group(1).strip() if match else None

            match = re.search(r'Traduction de\s*<a[^>]+auteur.asp\?NumAuteur=(\d+)[^>]*>(.*?)</a>', fiche, re.DOTALL)
            id_traducteur = match.group(1).strip() if match else None



            # Création d'un dictionnaire pour stocker les informations
            livre_info = {
                'titre': titre,
                'auteur': auteur,
                'titreoriginal' : titreoriginal,
                'anneeoriginale' : anneeoriginale,
                'illustration' : illustration,
                'traduction' : traduction,
                'serie' : serie,
                'tome' : tome,
                'categorie' : categorie,
                'collection' : collection,
                'collection_id' : id,
                'depotlegal' : depotlegal,
                'pages' : pages,
                'genre' : genre,
                'quatrieme' : quatrieme,
                'isbn' : isbn,
                'editeur' : editeur,
                'edition' : edition,
                'urlcouv' : urlcouv,
                # ID NOOSFERE
                'id_livre' : id_livre,
                'id_auteur' : id_auteur,
                'id_illustrateur' : id_illustrateur,
                'id_traducteur' : id_traducteur,
                'id_serie' : id_serie,
                'id_collection' : id_collection,
                'id_editeur' : id_editeur
            }

            # Convertir le dictionnaire en format JSON
            livre_json = json.dumps(livre_info, ensure_ascii=False, indent=2)

            # Afficher le JSON
            return livre_json
