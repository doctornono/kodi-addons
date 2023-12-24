from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import json

import re

url = "https://www.noosfere.org/livres/niourf.asp?numlivre=4161"

# Envoi de la requête HTTP
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urlopen(req)

# Vérification de la réussite de la requête
if response.getcode() == 200:
    # Analyse du contenu de la page avec BeautifulSoup et le parseur html.parser
    soup = BeautifulSoup(response.read(), 'html.parser')



    collection = ''
    collection_id = ''

    categorie = ''

    editeur =''
    edition = ''
    

    #ID NOOSFERE
    id_livre = 0
    id_auteur = 0
    id_illustrateur = 0
    id_traducteur = 0
    id_serie = 0
    id_collection = 0












    # Extraction des informations
    titre = soup.find('span', {'class': 'TitreNiourf'}).text.strip()
    auteur = soup.find('span', {'class': 'AuteurNiourf'}).text.strip()

    fiche = soup.find('span', {'class': 'ficheNiourf'})

    expression_reguliere = re.compile(r'Illustration de\s+<a[^>]+>(.*?)</a>', re.DOTALL)
    correspondance = expression_reguliere.search(str(fiche))
    if correspondance:
        illustration = correspondance.group(1).strip()
    else:
        illustration = ''


    expression_reguliere = re.compile(r'Traduction de\s+<a[^>]+>(.*?)</a>', re.DOTALL)
    correspondance = expression_reguliere.search(str(fiche))
    if correspondance:
        traduction = correspondance.group(1).strip()
    else:
        traduction = ''        


    # Extraction du cycle
    cycle_match = re.search(r'Cycle : <a[^>]+>(.*?)</a>', str(fiche), re.DOTALL)
    serie = cycle_match.group(1).strip() if cycle_match else None

    # Extraction du volume
    volume_match = re.search(r'vol\.\s+(\d+)', str(fiche))
    tome = volume_match.group(1).strip() if volume_match else None

    # Extraction de l'éditeur
    editeur_match = re.search(r'<a href="editeur.asp[^>]+>(.*?)</a>', str(fiche), re.DOTALL)
    editeur = editeur_match.group(1).strip() if editeur_match else None

    # Extraction de la collection
    collection_match = re.search(r'coll\.\s+<a[^>]+>(.*?)</a>', str(fiche), re.DOTALL)
    collection = collection_match.group(1).strip() if collection_match else None

    # Extraction du numéro de collection
    numero_collection_match = re.search(r'n°\s+(\d+)', str(fiche))
    collection_id = numero_collection_match.group(1).strip() if numero_collection_match else None

    sousfiche = soup.find('span', {'class': 'sousFicheNiourf'})

    expression_reguliere = re.compile(r'Dépôt légal : <a[^>]+>(.*?)</a>', re.DOTALL)
    correspondance = expression_reguliere.search(str(sousfiche))
    if correspondance:
        depotlegal = correspondance.group(1).strip()
    else:
        depotlegal = ''
    
    expression_reguliere = re.compile(r'(\d+) pages', re.DOTALL)
    correspondance = expression_reguliere.search(str(sousfiche))
    if correspondance:
        pages = correspondance.group(1).strip()
    else:
        pages = ''   
    
    expression_reguliere = re.compile(r'ISBN : (\S+)', re.DOTALL)
    correspondance = expression_reguliere.search(str(sousfiche))
    if correspondance:
        isbn = correspondance.group(1).strip()
    else:
        isbn = ''   

    expression_reguliere = re.compile(r'Genre : (\S+)', re.DOTALL)
    correspondance = expression_reguliere.search(str(sousfiche))
    if correspondance:
        genre = correspondance.group(1).strip()
    else:
        genre = '' 


    quatrieme = soup.find('div', {'id': 'quatrieme'})

    urlcouv = soup.find('img', {'name': 'couverture'})['src']





    # Création d'un dictionnaire pour stocker les informations
    livre_info = {
        'titre': titre,
        'auteur': auteur,
        'illustration' : illustration,
        'traduction' : traduction,
        'serie' : serie,
        'tome' : tome,
        'collection' : collection,
        'collection_id' : collection_id,
        'depotlegal' : depotlegal,
        'pages' : pages,
        'categorie' : categorie,
        'genre' : genre,
        'quatrieme' : str(quatrieme),
        'isbn' : isbn,
        'editeur' : editeur,
        'edition' : edition,
        'urlcouv' : urlcouv,
        # ID NOOSFERE
        'id_livre' : 0,
        'id_auteur' : 0,
        'id_illustrateur' : 0,
        'id_traducteur' : 0,
        'id_serie' : 0,
        'id_collection' : 0
    }

    # Convertir le dictionnaire en format JSON
    livre_json = json.dumps(livre_info, ensure_ascii=False, indent=2)

    # Afficher le JSON
    print(livre_json)

else:
    print("La requête a échoué. Statut de la requête :", response.getcode())
