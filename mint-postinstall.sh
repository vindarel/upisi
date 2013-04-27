#!/bin/sh

# #+gui:toggle=False

#: Programmes pratiques
sudo apt-get install -y terminator mplayer bash-completion git cclive htop tree ncdu python-pip

#+cat:Lecteurs Audio et Vidéo

#: Clementine
#+img:im/clementine.png
#+doc: Lecteur très pratique (et multiplateforme)
sudo apt-get install -y clementine

#: Smplayer


#+doc: Lecteur vidéo riche en options (téléchargement des sous-titres, lecture de youtube, …)
sudo apt-get install -y smplayer

#+end_cat
#+end:Lecteurs Audio et Vidéo

#+cat: Extensions du navigateur de fichiers
#+doc: Extensions de nautilus, le navigateur de fichiers.
#todo

#: Manipuler des images

#+img:im/nautilus-resize.jpg
#+doc: Convertir, changer des images de taille et autres manipulations accessibles directement dans Nautilus.
sudo apt-get install -y nautilus-image-converter


#+end_cat

#+cat: Internet
#: Ekiga, alternative à Skype
#+img:im/ekiga.png
#+doc: Ekiga permet de passer des appels audio et vidéo.
sudo apt-get install -y ekiga

#: Nicotine : télécharger de la musique en p2p
#+img:im/nicotine.png
#+doc: Logiciel qui permet de partager de la musique (ou autres) sur le réseau soulseek et d'aller en chercher chez les autres.
#
# Avec Soulseek, on va chercher la musique directement chez une personne, ce qui le distingue d'autres solutions de pair-à-pair, et de ce fait la vitesse de téléchargement est indépendante du nombre de personnes connectées.
sudo apt-get install -y nicotine

#+cat: Extensions Firefox
#+doc: Une sélection d'extensions Firefox pour éviter les mouchards sur le web ou télécharger des vidéos.

#+sh: Bloquer plein de mouchards
firefox ghostery &

#+sh: Télécharger vidéos youtube
firefox && echo foo && videodownloader &

#+end_cat


#+end_cat