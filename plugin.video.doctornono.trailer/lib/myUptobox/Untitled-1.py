import lxml.etree as et

tree = et.parse(r'J:/recalbox/roms/mame/gamelist.xml')
tree = tree.getroot()
# Trier les jeux par nom
tree[:] = sorted(tree, key=lambda ch: ch.xpath("name/text()"))

# Ajout du chemin par défaut de la video
for game in tree.findall('game'):
    if game.xpath('/video'):
        print(game.tag, game.tag)
    else:
        video = et.SubElement(game, 'video')
        nom = game.find('path')
        nom = str(nom.text)
        video.text = '/media/videos/' + nom.replace('zip', 'mp4')

# Remplacer les mauvais chemins ./ par rien



#print(et.tostring(tree).decode("utf-8"))




etr = et.ElementTree(tree)
etr.write(r'J:/recalbox/roms/mame/gamelist_new.xml', pretty_print=True, xml_declaration=True, encoding="utf-8", standalone="yes")