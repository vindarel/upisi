#!/bin/sh

#+ Premier soft
sudo apt-get install one

#+cat: Cat one
#+second soft

echo un bis

#+cat: Sous cat
echo un tierce
#+end_cat
#+ apres sous cat
#+doc: cette commande est placée entre deux
#catégories.
echo deux bis : apres sous cat

#+end_cat
echo deux : apres cat