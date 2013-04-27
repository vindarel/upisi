upisi
=====

the Universal Post-Installation Scripts Interface

En développement.


Usage :

- écrire un script bash de post-installation de la forme :
  apt-get install foo bar
  echo do something

- utiliser des tags spéciaux en commentaire pour agir sur l'interface Gtk :
  - #+title: un titre
  - #+doc: de la documentation sur l'élément suivant
  - #+begin … #+end : regroupe plusieurs commandes shell
  - #+gui:toggle=False : indique à l'interface de ne pas sélectionner cet élément par défaut.

- lancer python upotism.py <votre script.sh> gui.glade


Dév :
- postinstaller.py : parser du script
- gui.glade : interface graphique Gtk+3 (utiliser avec glade)
- upotism.py : programme principal
- utils.py : méthodes annexes
- data_test_scrip.sh : exemple complet de script possible