#!/bin/sh

#+gui:toggle=False


#: Programmes pratiques
sudo apt-get install -y terminator mplayer bash-completion git cclive htop tree ncdu python-pip soundconverter nautilus-open-terminal

#+cat:Lecteurs Audio et Vidéo

#: Clementine
#+im:im/clementine.png
#+doc: Lecteur très pratique (et multiplateforme)
sudo apt-get install -y clementine

#: Smplayer


#+doc: Lecteur vidéo riche en options (téléchargement des sous-titres, lecture de youtube, …)
sudo apt-get install -y smplayer

#+end_cat lecteurs

#+cat: Extensions du navigateur de fichiers
#+doc: Extensions de nautilus, le navigateur de fichiers.
#todo

#: Manipuler des images

#+im:im/nautilus-resize.jpg
#+doc: Convertir, changer des images de taille et autres manipulations accessibles directement dans Nautilus.
sudo apt-get install -y nautilus-image-converter


#+end_cat extensions nautilus

#+cat: Internet

#: Ekiga, alternative à Skype
#+im:im/ekiga.png
#+doc: Ekiga permet de passer des appels audio et vidéo. (il existe également Linphone et Jitsi).
sudo apt-get install -y ekiga

#: Nicotine : télécharger de la musique en p2p
#+im:im/nicotine.png
#+doc: Logiciel qui permet de partager de la musique (ou autres) sur le réseau soulseek et d'aller en chercher chez les autres.
#
# Avec Soulseek, on va chercher la musique directement chez une personne, ce qui le distingue d'autres solutions de pair-à-pair, et de ce fait la vitesse de téléchargement est indépendante du nombre de personnes connectées.
sudo apt-get install -y nicotine

#: Thunderbird, client mail
#+doc: Essayez Thunderbird au lieu de rester dans votre interface web, vous ne serez pas déçu-e ! On peut gérer plusieurs boites mail en même temps, et si vous souhaitez un fonctionnement vraiment proche de gmail, vous pouvez installer l'extension «conversation». On peut également se créer une adresse mail libre (menu Fichie > Nouveau > Obtenir un nouveau compte courrier).

aptitude install -y thunderbird

#: Liferea, lecteur de flux RSS
#+im:im/liferea.png
#+doc: Un lecteur de flux RSS est très pratique quand on commence à suivre quelques blogs ou sites d'informations.
aptitude install -y liferea


#: Dropbox
#+doc: Dropbox permet de synchroniser et partager des fichiers «dans les nuages».

aptitude install -y nautilus-dropbox

#+cat: Extensions Firefox
#+doc: Une sélection d'extensions Firefox pour éviter les mouchards sur le web ou télécharger des vidéos.

#+sh: Bloquer les publicités
#+doc: AdBlock-plus permet de bloquer les encarts publicitaires sur internet, les publicités avant les vidéos youtube, etc.

firefox https://addons.mozilla.org/fr/firefox/addon/adblock-plus/?src=search  &

#+sh: Bloquer plein de mouchards
#+doc: Ghostery protège votre vie privée. Il permet de bloquer énormément de trackers tels que les boutons Facebook+1, les statistiques de google, toutes les agences de publicité, etc. Plus d'infos : [http://ghostery.foo | site officiel]

firefox https://addons.mozilla.org/en-US/firefox/addon/ghostery/ &

#+sh: Télécharger les vidéos de youtube (et du net)
firefox https://addons.mozilla.org/en-US/firefox/addon/video-downloadhelper/  &

#+sh: Web Of Trust
#+im:im/clementine.png
#+doc: WOT permet d'être averti lorsqu'on visite un site malfaisant.

firefox https://addons.mozilla.org/en-US/firefox/addon/wot-safe-browsing-tool/ &

#+end_cat #extensions firefox ###############################


#+end_cat #internet


#+cat: Retouche photo et vidéo


#: Gimp, retouche photos
#+doc: Gimp est l'équivalent de Photoshop, en libre. Comme Photoshop, il faut apprendre un peu à l'utiliser ! (un exemple : le site [ http://www.1point2vue.com | Un Point de Vue]).
# Le paquet gimp-plugin-registry installe des filtres et scripts supplémentaires.

apt-get install -y gimp gimp-plugin-registry


#: Fotowall, patchworks de photos
#+im:im/fotowall.png
#+doc: Fotowall permet d'assembler des photos ensemble (un peu à la manière de Picasa).
aptitude install -y fotowall


#: Openshot, montage vidéo
#+gui:toggle=False
#+doc: Openshot est le meilleur logiciel de montage vidéo sous linux actuellement (il existe aussi Kdenlive).

#+im:im/openshot.png

aptitude install -y openshot

#+end_cat


########################################
#+cat: Documentation

#+begin: Critiques et altenatives de Facebook
#+doc: Si vous avez déjà pensé à supprimer votre compte Facebook, bravo ! Pour comprendre tous les enjeux et connaître des réseaux sociaux alternatifs différents (tout en gardant un œil critique), [http://sortirdefacebook.wordpress.com|cette brochure est faite pour vous].

firefox https://sortirdefacebook.wordpress.com/ &
wget pdf

#+end

#+begin: Truth Happens (vidéo)
#+doc: «D'abord, ils nous ignorent. Ensuite, ils se moquent. Et ils nous combattent» M. Gandhi. Une vidéo de Red Hat, éditeur milliardaire de logciels libres, éditeur de la distribution Fedora.

cclive http://truth-happens.com -O ~/Truth-happens.flv &
firefox http://truth-happens.com &

#+end

#+ Manuel de Gimp
wget gimp

#+ Manuel de programmation Shell
wget shell

#+ Manuel de programmation Python
wget python

#+end_cat Documentation


#+sh: truth happens
#+doc: la ligne suivante ne marche pas avec un item normal, il faut préciser que c'est une commande shell.
aptitude install -y cclive && cclive http://truth-happens.com

#: mettre à jour le système
#+doc: Cet élément lancera le gestionnaire graphique de mises à jour.
aptitude update && aptitude upgrade -y
