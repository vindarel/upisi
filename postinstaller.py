#! /usr/bin/python
# -*- coding: utf-8 -*-

# 3 déc 2012


# TODO: vérifier la correction des nested cats

import sys

TO_INSTALL = []
# ITEMS = []
"""Items : liste de dictionnaires avec au moins un title puis apps, doc, sh, lines.
"""
CATS = []
"""Catégories : liste de dicos cat:un titre, items:liste d'items.
plus besoin non ? 2-fév … peut être que si pour l'affichage toggle 9 fév
"""

OPTIONS = {'gui_toggle':True} # toujours utile ?
# _TOGGLE_COUR = True
TOGGLE_DICT = {}

_ITEM = '#+ '
_ITEM2 = '#:'
_SH = '#+sh:'
_CAT = '#+cat:'
_END_CAT = '#+end_cat'
_DOC = '#+doc:'
_BEGIN = '#+begin:'
_END = '#+end'
_IGNORE = '#+ignore'

_GUI = '#+gui'
_GUI_TOGGLE = _GUI+':toggle='

_IMG = '#+img:'
"""Display local or remote images for the given element."""

_PACKMAN = None
# options globales : toujours utiles ? (non, il n'y en a plus de globales)
# _OPTION_GUI = '#+GUI'
# _OPTION_GUI_TOGGLE = _OPTION_GUI+':toggle_default='


def printitems(ITEMS, prefixe=""):
    i = 1
    for app in ITEMS:
        print prefixe, i, ; i+=1
        if 'cat' in app.keys():
            print 'On a une cat: ' + app['cat']
            printitems(app['items'], prefixe=prefixe + "\t")

        print prefixe + ', '.join( [ "%s: %s" % (k, v) for k,v in app.items()] )


def multiline(f, line):
    """Rassemble une ligne coupée avec des \n en une seule. Saute les lignes vides et renvoie la prochaine ligne non-vide. Si la ligne courante se fini par un backslach (et aussi par
    un \n), lis aussi la ligne suivante.
    """
    while line.endswith('\\\n'):
        line = line[0:-2] # enlever le \ et le \n
        line += ' ' + f.readline()

    return line

def nextline(f,ignore_comments = False):
    """Renvoie la prochaine ligne qui n'est pas une ligne vide."""
    # faire attention aux trailing spaces ?
    to_ignore = ['\n',]
    #ne marche pas

    if ignore_comments == True:
        print 'il faut ignorer les commentaires'
        to_ignore.append_regexp('regexp')

    line = f.readline()
    if not line:
        # printitems()
        # exit(0)
        return 'EOF'

    while line == '\n':
        line = f.readline()
        if not line:
            exit(0)

    return line

# def parse_options(f):
#     # Options are at the beginning of the file, before any declaration of item.
#     line = f.readline()
#     while line.startswith('#'):
#         if line.startswith(_OPTION_GUI):
#             if line.startswith(_OPTION_GUI_TOGGLE):
#                 if '=True' in line:
#                     OPTIONS['gui_toggle'] = True
#                 elif '=False' in line:
#                     OPTIONS['gui_toggle'] = False
#                 else:
#                     print 'Unknown global option "%s"' % line

#         line = f.readline()


def getapps(line):
    """Découper la ligne après avoir reconnu le gestionnaire de
    paquets (nécessite toujours un appel à is_call_to_package_manager
    avant), ajouter les applications dans la liste globale si elles
    n'y sont pas déjà puis retourner la liste des applications.
    """
    if not  _PACKMAN:
        print "ERROR : we didn't recognize any package manager. No packages will be installed." # ne devrait logiquement pas arriver car on appelle is_call_to_package_manager avant tout appel à getapps.
        return []

    # couper 'aptitude install' ou 'pacman -S', que la ligne commence avec su ou sudo
    line = line[ line.index(_PACKMAN) + len(_PACKMAN) + 1 : ]

    # dans le cas où on avait l'option -y:
    if line.startswith('-y'):
        line = line[2:].strip()

    # il faudra trouver qc de plus générique pour gérer d'autres options…
    if line.startswith('--assume-yes'):
        line = line[len('--assume-yes') + 1 :].strip()

    # dans le cas où la ligne avait commencé par su -c "yum install
    # foo bar" il reste un "
    if line.endswith('"') or line.endswith("'"):
        line = line[ : -1 ]

    # il est possible qu'on ait un commentaire
    if '#' in line:
        line = line[: line.index('#')]

    packages = line.split()
    apps = []
    for elt in packages:
        if elt not in apps:
            TO_INSTALL.append(elt)
            apps.append(elt)

    return apps


    # eltline = line.split()
    # # on coupe tout ce qui est avant 'install'
    # if 'install' in eltline:
    #     apps = []
    #     elts = eltline[eltline.index('install') + 1:]
    #     for e in elts:      # TODO list comprehension ?!
    #         if e not in TO_INSTALL:
    #             TO_INSTALL.append(e)
    #             apps.append(e)

    #     return apps

    # else:
    #     print "on ne voit pas install dans la ligne : rien à installer."

def get_doc(f, line):
    """Tout ce qui est un commentaire est inclu dans la doc, jusqu'à la prochaine ligne qui n'est pas un commentaire."""
    doc =""

    #  Il est bien plus facile d'utiliser un second descripteur de fichier pour regarder la ligne suivante :
    g = open(f.name, 'r')
    g.seek(f.tell())

    while line.startswith('#') and not line.startswith(_GUI) and not \
            line.startswith(_IMG):

        doc +=  line[len(_DOC) :].strip() if _DOC in line else line[1:].strip()
        doc += ' '
        # gline = nextline(g).strip()
        gline = g.readline().strip()
        if gline.startswith('#') and not gline.startswith(_GUI) and not \
                line.startswith(_IMG):
            # line = nextline(f).strip()
            line = f.readline().strip()
        else:
            # pour la lecture de la doc d'une cat, ne PAS avancer la tête de lecture.

            return (gline, doc)


    return (line, doc)


def get_title(line):
    """Le titre est la chaine après le dernier caractère ':'"""
    pass

def is_call_to_package_manager(line):
    """Renvoie True si la ligne commence par 'sudo apt-get install', où apt-get peut être un autre package manager (yum, equo, aptitude,…)."""

    # Tous la même chose : peuvent être précédées par su et ses variantes su -C ou sudo. Mais l'essentiel est qu'on a 'foo install' dans la ligne.
    if line.startswith('#'):
        return False

    _managers = ['aptitude install', 'apt-get install', 'yum install', 'equo install', 'pacman -S', 'yaourt -S', 'urpmi', 'zypper install',]

    #regarder toutes les solutions et regrouper les paquets dans une
    #liste permet d'utiliser un script fait pour debian sous fedora
    #par exemple. Même si cela ne devrait pas arriver.
    global _PACKMAN
    for packman in _managers:
        if packman  in line:
            _PACKMAN = packman
            return True

    return False

    # if line.startswith("sudo aptitude install") or line.startswith('aptitude install') or \
    #         line.startswith('sudo apt-get install') or line.startswith('apt-get install') or \
    #         line.startswith('yum install') or line.startswith('sudo yum install'):
    #     return True

    # else:
    #     return False



def parser(f, end_pattern=None, toggle=True):
    """TODO mettre en place doctest ? unitest ?"""

    _TOGGLE_COUR = toggle
    # _APT_LIKE = 'sudo aptitude'

    ITEMS = []
    # parse_options(f)
    while True:
        # début changements nextline
        line = nextline(f)

        if line == 'EOF':
            return ITEMS

        if end_pattern:
            if line.startswith(end_pattern):
                return ITEMS


        # Lignes simples, sans titre explicite.  Le titre devient la
        # suite de programmes (qui ne sont pas en doubles)
        if is_call_to_package_manager(line):
        # if line.startswith("sudo aptitude install") or line.startswith('aptitude install') or \
                # line.startswith('sudo apt-get install') or line.startswith('apt-get install'):
            #  ne pas se cantonner à reconnaitre apt, mais aussi yum, yaourt et les autres.
            # import platform
            # platform.platform -> Linux … pae…LinuxMint Debian
            line = multiline(f, line)
            # Nouvel item :
            apps = getapps(line)

            title = ' '.join(elt for elt in apps)
            item = {'title':title, 'apps':apps,
                    'gui_toggle':_TOGGLE_COUR}
            ITEMS.append(item)

        # Une suite de commandes shell encadrées par #+sh: titre éventuel
        #  plus #+begin et #+end éventuels si sur plusieurs lignes
        elif line.startswith(_SH):
            # en fait on a une commande shell si on n'a rien reconnu…
            title = line[len(_SH) :].strip()
            item  = {'title':title}

            line = f.readline()

            if line.startswith(_DOC):
                # doc = line[len(_DOC) :].strip()
                line, doc = get_doc(f, line)
                item['doc'] = doc
                line = nextline(f).strip()


            # line = nextline(ignore_comments = True)
            while line.strip().startswith('#') or \
                    line.strip() is '' or line.startswith('\\n'):
                line = f.readline()

            # ITEMS.append({'title':title,
                          # 'gui_toggle':_TOGGLE_COUR,
                          # 'sh': [line.strip(),]  })
            item['gui_toggle'] = _TOGGLE_COUR
            item['sh'] = [line.strip(),]
            ITEMS.append(item)
            # line = nextline()   # sans cette ligne -> pb avec apps TODO

        # Une suite de commandes shell
        elif line.startswith(_BEGIN):
            # attention que les commandes doivent être exécutées en UNE fois,
            # et pas ligne après ligne (if, then, else, …)
            commands = []
            commands.append("")


            title = line[len(_BEGIN) :].strip()
            item = {'title':title, 'gui_toggle':_TOGGLE_COUR}

            line = nextline(f)
            while not line.strip() ==  _END:
                # commands.append(line.strip())
                commands[0] += "\n" + line.strip()
                line = nextline(f)

            item['sh'] = commands

            ITEMS.append(item)


        # On détecte un titre, donc un nouvel item.
        elif line.startswith(_ITEM) or line.startswith(_ITEM2):
            item = {'title':line[2:].strip()}
            item['gui_toggle'] = _TOGGLE_COUR
            ITEMS.append(item)

            # line = f.readline() # ou nextline ??
            line = nextline(f)

            # Ce if est 'nesté' car on veut rester sur le même item

            # attention: en ajoutant un attribut dans le or, ne pas
            # oublier de le rajouter dans get_doc
            while line.startswith(_DOC) or line.startswith(_GUI) or \
                    line.startswith(_IMG):
                if line.startswith(_DOC):
                    # doc = line[len(_DOC) :].strip()
                    line, doc = get_doc(f, line)
                    item['doc'] = doc
                    line = nextline(f).strip()

                if line.startswith(_GUI):
                    if line.startswith(_GUI_TOGGLE):
                        if 'True' in line:
                            item['gui_toggle'] = True
                        elif 'False' in line:
                            item['gui_toggle'] = False
                        else:
                            print "Option %s inconnue.", line

                    else:
                        pass

                    line = nextline(f)


                if line.startswith(_IMG):
                    img = line[len(_IMG) : ]
                    item['img'] = img
                    line = nextline(f)

            if is_call_to_package_manager(line):
                # Lire la ligne suivante si on trouve un \
                line = multiline(f, line)

                item['apps'] = getapps(line)

            else:
                item['sh'] = [line.strip(), ]

        # - fin nouvel item et doc et sudo nestés -
        # toggle par défaut pour les éléments suivants.
        # Surtout utile pour la récursion des catégories.
        elif line.startswith(_GUI):
            if line.startswith(_GUI_TOGGLE):
                # global _TOGGLE_COUR #todo test debug
                if 'True' in line:
                    _TOGGLE_COUR = True
                elif 'False' in line:
                     _TOGGLE_COUR = False
                else:
                    print 'Option inconnue : %s' % line

        # Détecter une catégorie
        # Elle a sa propre liste d'items
        elif line.startswith(_CAT):
            cat_title = line[len(_CAT) :] #.strip() non, car il faut absolument le même titre avec le même nombre d'espaces pour trouver la fin.

            cat = {'cat':cat_title.strip()}

            if line.startswith(_DOC):
                line = nextline(f)
                line, doc = get_doc(f, line)
                # la tête de lecture ne doit PAS pointer sur la prochaine ligne (car on appelle récursivement le parser qui va effectuer un nextline)
                cat['doc'] = doc

            # Get list of items of the category recursively :
            # items = parser(f, end_pattern=_END+':'+cat_title,
            items = parser(f, end_pattern=_END_CAT,
                           toggle=_TOGGLE_COUR) # attention au ':'
            cat['items'] = items
            cat['gui_toggle'] = _TOGGLE_COUR

            ITEMS.append(cat)
            CATS.append(cat_title.strip())



        elif line.startswith(_IGNORE):
            print 'TODO: ' + _IGNORE

        else:
            if not line.startswith('#'):
                # on n'a pas reconnu cette ligne avant, donc c'est une commande shell
                #TODO la mettre dans une liste (pour affichage multiligne)
                ITEMS.append({'title':line.strip(),
                              'gui_toggle':_TOGGLE_COUR,
                              'sh': [line.strip(),] })


def main(script):
    """Ouvre le fichier donné en lecture, parcoure le script et rempli
 les listes CATS et ITEMS. Retourne la liste d'ITEMS. CATS est
 accessible via postinstaller.CATS.

    Arguments:
    - `script`: fichier du script à analyser. Fichier ouvert en lecture.
    """
    ITEMS = parser(script)
    # printitems(ITEMS)
    return ITEMS



if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        script = open(sys.argv[1], 'r')
        items = main(script)
        printitems(items)

    else:
        print 'Usage : donnez un script à analyser en argument.'

        # ITEMS = parser(f=script)
        # printitems(ITEMS)


