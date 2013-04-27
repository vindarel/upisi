#!/bin/sh

# Exemple de fichier de post-install qui sera parsé par «upostin», avec les commandes pour donner du sens


# Variables qui s'applique pour tous les éléments jusqu'à nouvel ordre
# (déf dans une catégorie ou pour un item particulier)
# Cocher les cases par défaut ? True/False
#+gui:toggle=False
#

# Un énoncé pour ce programme :
#: Liferea, lecteur de liens RSS
#+doc:Liferea est un lecteur de flux RSS. S'abonner à un flux RSS est un peu comme s'abonner à un journal, mais pour un site ou un blog. Cela permet d'être automatiquement tenu au courant quand un nouvel article est posté.
#Quand on visite réguliièrement un site, on n'en a pas besoin, mais quand on veut surveiller plus d'une dizaine de sites cela devient vraiment pratique.

sudo aptitude install liferea
#TODO: pb avec cette ligne et foo

#: Devede, créer des DVDs
#+gui:toggle=True
sudo aptitude install devede
#+gui:toggle=False
#: Libreoffice, complet, en français
sudo aptitude install libreoffice librepresentations \
    libre-fr \
    libre-trois

# On ajoute simplement des programmes.  Cette ligne doit être lue
# correctement, mais le «sudo apt-get install» ne doit pas être inclu
# dans la liste des programmes à installer.
sudo apt-get install emacs foo third cmus-remote
# La même, on ajoute aptitude qui doit être installé, les autres ne
# doivent pas être comptés en doublons.
sudo apt-get install aptitude emacs foo third cmus-remote

# idem, sur plusieurs lignes :
sudo aptitude install eins zwei drei\
   seconde-ligne cinq \
    troisieme_ligne.345.bar

# et ça va pour le moment :)
# Et c'est fait ! 7 déc 12, bossé 2h

# La suite : doc, sh avec begin et end, les catégories

#+ Un titre avec autre syntaxe
sudo aptitude install titre_ok

#: En apprendre plus sur Jabber
#+doc:http://www.jabberfr.org/
sudo aptitude install jabber

#+ Encore un peu de  Jabber
#+doc: vous pouvez voir le site suivant : [http://www.jab-plus.org|en savoir plus]
# todo bug si pas cette ligne
sudo aptitude install jabber-sans-doc
# la doc doit être au-dessus, après le titre.



#+sh: des commandes shell, ou une seule ?
# On reconnait par défaut une seule ligne. Plusieurs avec begin et end.

echo salut le monde

#+begin: une suite de commandes
echo ligne 1
echo ligne 2
#+end

# ici, une commande toute seule
firefox 'url'

# tout fait, 14 décembre

#+gui:toggle=False
#+cat:ma cat
#+doc: doc de la cat.
#On fait plein de choses dans cette cat.

sudo aptitude install entre cat et sous-cat

#+cat: sous-cat
#+doc: voici la doc de…
#la sous-cat.
une sous cat
et ça marche
#+end: sous-cat
# mettre exactement le même titre, attention aux espaces.

#+gui:toggle=False
touch foo_example_file1.txt
sudo touch foo_example_file2.txt
sudo aptitude install ligne_3 dans_cat


aptitude install apres-sous-cat

#+end:ma cat

#+ dernier item apres une cat
sudo aptitude install apres-cat
