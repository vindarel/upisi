#! /usr/bin/python
# -*- coding: utf-8 -*-

# étudier mintinstall
# parser le fichier et passer les infos à mintinstall, qui prend en charge tout le reste ?


import postinstaller
import utils

from gi.repository import Gtk

import sys
import os
import tempfile
from subprocess import Popen, PIPE

GLADEFILE = 'gui.glade'

WELCOME = 'Bienvenue dans Upisi. Cliquez sur un élément de la gauche pour savoir ce qu\'il va installer, ou cliquez sur suivant.'

_VERSION = '0.1'
_SYNAPTIC_PATH = "/usr/sbin/synaptic"

def print_tree_store(store):
    rootiter = store.get_iter_first()
    print_rows(store, rootiter, "")

def print_rows(store, treeiter, indent):
    while treeiter != None:
        print indent + str(store[treeiter][:])
        if store.iter_has_child(treeiter):
            childiter = store.iter_children(treeiter)
            print_rows(store, childiter, indent + "\t")
        treeiter = store.iter_next(treeiter)



def cellRenderer_func(column, cellRenderer, treeModel, treeIter, userData):
    """Cell data function, pour contrôler l'état de UNE ligne du CellRendererText, afin de le mettre en état 'inconsistent' si les éléments fils ne sont pas tous dans le même état."""
    title_cour = treeModel.get_value(treeIter, 0)

    if title_cour  in postinstaller.CATS:
        iter_next = treeModel.iter_children(treeIter)

        # si on a  tout de suite encore une cat
        if treeModel.iter_has_child(iter_next) and \
                treeModel.get_value(treeModel.iter_children(iter_next), 0) in postinstaller.CATS:
            etat = cellRenderer_func(column, cellRenderer, treeModel,
                                     treeModel.iter_children(iter_next), userData)
            print 'etat du fils:', etat
            if etat == None:
                cellRenderer.set_property('inconsistent', True)
                return None
            elif etat == True:
                treeModel.set_value(treeIter,1, True)
            else:
                treeModel.set_value(treeIter, 1, False)


        # On regarde quel est l'état du premier élément de la cat (il y en a au moins un).
        # On parcours tous les éléments de la cat, et si on trouve qln avec le même état, on retourne Inconsistent (None).

        # toggled = treeModel.get_value(iter_next, 1)
        # Regarder récursivement : il est possible qu'on tombe encore sur une catégorie.
        toggled = cellRenderer_func(column, cellRenderer, treeModel, iter_next, userData) #essentiel d'appeler la fonction si on a une suite de cat
        if toggled == None:
            cellRenderer.set_property('inconsistent', True)
            return None

        iter_next = treeModel.iter_next(iter_next)

        while iter_next:

            etat_elt = cellRenderer_func(column, cellRenderer, treeModel, iter_next, userData)
            if etat_elt == None:
                cellRenderer.set_property('inconsistent', True)
                return None

            elif etat_elt != toggled:
                cellRenderer.set_property('inconsistent', True)

                return None

            else:
                iter_next = treeModel.iter_next(iter_next)



        return toggled

    else:
        cellRenderer.set_property('inconsistent', False)
        return treeModel.get_value(treeIter, 1)




class PostInstaller:
    """Interface au parser de script de post-installation."""

    labels = {}
    TO_INSTALL = []
    """liste de apps à installer"""

    TO_EXEC = []
    """liste de commandes à exécuter"""

    DO_UPGRADE = False


    # TODO j'ai rentré cette méthode dans la classe, donc je peux enlever les arguments et utiliser self.arg à la place. 11 fév
    def insertTreeModel(self, treeModel, items, levelIter=None, renderer_toggle=None,
                    column=None):
        """Insère des éléments récursivement dans le modèle treeModel.
        Arguments:

        - `treeModel`: le modèle en arborescence du treeview dans lequel insérer les éléments
        - `levelIter`: un itérateur de treeModel, permet d'insérer récursivement. Par défaut, insère dans le premier niveau de l'arborescence.
        - `items`: liste d'items (comportant title, apps, sh, cat,…)
        """

        for item_cour in items:


            # Fonction à être appelée pour chaque ligne du CellRendererToggle
            # C'est elle qui détermine si la case est cochée ou inconsistente.
            column.set_cell_data_func(renderer_toggle, cellRenderer_func, items)

            if 'cat' in item_cour:
                toggle = item_cour['gui_toggle']
                treeIter = treeModel.append(levelIter, [ item_cour['cat'],toggle ])
                self.insertTreeModel(treeModel, item_cour['items'],
                                     levelIter=treeIter,
                                     renderer_toggle=renderer_toggle, column=column)


            else:
                if not 'title' in item_cour:
                    print 'Error : we must have set a title before'
                    item_cour['title'] = 'Not title set, title must have been set before for the elt ' + item_cour

            if 'title' in item_cour:
                toggle = item_cour['gui_toggle'] if (item_cour.has_key('gui_toggle')) else postinstaller.OPTIONS['gui_toggle']

                treeIter = treeModel.append(levelIter, [ item_cour['title'],toggle ]) # coché par défaut TODO : controler case cochée ou pas-> supprimable ?

            # Non : si on fait comme ça (avec treeModel.append), les
            # apps et les sh vont avoir une case toggle à cocher, et
            # ce n'est pas ce que l'on veut. TODO simplement
            # désactiver le bouton toggle ? -> il semblerait qu'on ne
            # peut pas la cacher en fonction de la ligne. Si non :
            # cliquer sur un item de haut-niveau coche toute
            # l'arborescence, et on ne peut pas dé-cocher un élt
            # simple.

                # if 'apps' in item_cour:
                #     myapps = ', '.join( ['%s' % app for app in item_cour['apps'] ])
                #     treeModel.append(treeIter, [myapps, None])

                # if 'sh' in item_cour:
                #     mysh = '\n'.join( ['%s' % sh for sh in item_cour['sh'] ])
                # #TODO si on a apps ET sh, comment représenter les données ?
                #     treeModel.append(treeIter, [mysh, None])

                # # if 'begin'  in item_cour:
                #     # # plus besoin, le begin est stocké dans sh
                #     # mysh = '\n'.join( ['%s' % sh for sh in item_cour['begin'] ])
                #     # treeModel.append(treeIter, [mysh, None])

                # if 'doc' in item_cour:
                #     # import ipdb; ipdb.set_trace()
                #     pass

    def open(self, script):
        """Ouvre un fichier. Initialise le treeModel et lance le parser sur le script.

        `script`: fichier ouvert en lecture.
        """

        # Déf
        self.treeModel = Gtk.TreeStore(str, bool)
        # Ce serait pratique de donner la liste des apps et des sh en
        # paramètre du treeModel. Comme cela le lien entre l'affichage et les
        # données est fait, et pas besoin de parcourir toute la liste
        # des items à chaque fois. Mais on ne peut pas donner de type list. On peut
        # donner un objet. Mais moi j'utilise des listes…

        # Remplissage avec les données récupérées par le script

        # self.ITEMS = postinstaller.main(script, file_name='data_test_script.sh') #passer le nom du fichier pour utiliser un second lecteur de ligne
        self.ITEMS = postinstaller.main(script) # peut être pas la meilleure chose d'exécuter ceci ici ?


        # Lier le modèle nouvellement créé à la vue créée avec glade :
        self.treeview1.set_model(self.treeModel)

        # Insertion des données dans le treeview1 : (récursif)
        self.insertTreeModel(self.treeModel, self.ITEMS, None, self.renderer_toggle, self.column)


    def __init__(self, script):

        # Set the Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADEFILE)


        # dict de signaux. On peut aussi utiliser une classe dont les
        # méthodes sont les noms des signaux. Voir les signaux dans le .glade (handle)
        dic = {
            "on_button1_clicked" : self.btnValidate_clicked,
            "on_button2_clicked" : self.on_button2_clicked,
            "on_MainWindow_destroy" : self.quit,
            "on_window1_delete_event" : self.quit,
            "on_apropos_select" : self.on_apropos_select,
            "on_apropos_activate" : self.on_apropos_activate,
            "on_openfile_activate" : self.on_openfile_activate,
            "on_menu_quit_activate" : self.on_menu_quit_activate,
            "on_open_url_activate" : self.on_open_url_activate,

            }

        self.builder.connect_signals(dic)

        self.window = self.builder.get_object("window1")

        # en cours
        self.im = self.builder.get_object('image1')
        self.images = {}
        # self.im.set_from_file('../../Images/gaston.jpg')
        # import ipdb; ipdb.set_trace()

        # Récupérer l'objet créé avec glade :
        self.treeview1 = self.builder.get_object("treeview1")

        self.expander = self.builder.get_object("expander1")

        # Afficher des choses dans la frame2
        self.frame2 = self.builder.get_object('frame2')

        # Le label est à l'intérieur de la frame2 (laquelle comporte
        # son label pour un titre, qui ne peut pas aller sur plusieurs
        # lignes)
        self.label = self.builder.get_object('label2')
        self.frame2.set_label( 'Documentation')

        self.label.set_text(WELCOME)


        # Construire les colonnes de l'interface :
        renderer = Gtk.CellRendererText()
        # colonne titre
        self.column = Gtk.TreeViewColumn("Titre", renderer, text=0)
        self.treeview1.append_column(self.column)
        #  colonne toggle
        self.renderer_toggle = Gtk.CellRendererToggle()
        self.renderer_toggle.connect("toggled", self.on_cell_toggled, self.renderer_toggle)
        column_toggle = Gtk.TreeViewColumn("Installer", self.renderer_toggle, active=1)
        self.treeview1.append_column(column_toggle)

        # selection et signaux ? TODO…
        self.select = self.treeview1.get_selection()
        self.select.set_mode(Gtk.SelectionMode.BROWSE) # un seul élt sélectionné, ne peut pas dé-sélectionner
        # select.set_mode(Gtk.SelectionMode.MULTIPLE) # il faut changer le callback TODO


        # Notifie quand on clique sur n'importe quelle ligne
        self.select.connect("changed", self.on_tree_selection_changed)

        # Pour parcourir TOUT l'arbre, il faut utiliser pint_tree_store
        # print_tree_store(self.treeModel)

        # Appeler le parser sur le script et afficher les données dans l'interface :
        self.open(script=script)

        self.window.show_all()

    def on_apropos_select(self):
        """

        Arguments:
        - `self`:
        """
        print 'signal on_apropos_select'

    def on_apropos_activate(self, image):
        """
        Afficher la fenêtre d'à propos.
        """
        self.apropos = self.builder.get_object('aboutdialog1')
        self.apropos.set_license('GNU General Public Licence v.3')
        self.apropos.set_version(_VERSION)

        retValue = self.apropos.run()
        if retValue == -6:      # close button
            self.apropos.hide()
        else:
            print 'retValue de A propos = ', retValue # debug
            self.apropos.hide()


    def on_menu_quit_activate(self, truc):
        """

        """
        Gtk.main_quit()

    def on_open_url_activate(self, truc):
        self.dialog_url = self.builder.get_object('dialog-open-url')
        ret = self.dialog_url.run()


        if ret == 0:            # ok button
            self.entry_url = self.builder.get_object('entry-url')
            url = self.entry_url.get_text()
            file_url = utils.dl_url(url)

            if not file_url:
                print "Impossible d'ouvrir le fichier associé à cette url %s" % url
                self.dialog_url.hide()
                self.display_dialog("Impossible d'ouvrir cette url")

            else:
                self.dialog_url.hide()
                to_open = open(file_url, 'r')
                self.open(to_open)




    def on_openfile_activate(self, truc):
        """Ouvrir un nouveau script.
        """

        self.filechooser = self.builder.get_object('filechooser')

        # Filtres pour la sélection :
        filter_sh = Gtk.FileFilter()
        filter_sh.set_name("Scripts shell")
        filter_sh.add_pattern("*.sh")
        self.filechooser.add_filter(filter_sh)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        self.filechooser.add_filter(filter_any)

        ret = self.filechooser.run()

        if ret == 0:
            chosenfile = self.filechooser.get_filename()
            self.filechooser.hide()
            script = open(chosenfile, 'r')
            self.open(script)

        else:
            self.filechooser.hide()



    def get_item(self, path):
        """path = une str obtenue avec self.treeModel.get_path(iter).to_string().
        Retourne un item, c'est à dire un dico avec title, apps, etc."""

        items = self.ITEMS

        while ':' in path:
            left = int( path[0:path.index(':')] )
            path = path[ path.index(':') + 1 :]
            items = items[left]['items']

        return items[int(path)]



    def on_tree_selection_changed(self, selection):
        """On sélectionne une ligne : on affiche la documentation de
        l'élément et son image associée."""

        def get_doc(path, items):
            """Colle les docs des éléments récursivement, dans le cas d'un path de la forme '0:1:2:x:y' (string).
            Retourne la documentation de tous ces éléments.
            """

            # code redondant avec get_item et get_apps ?
            if ':' in path:
                left = int( path[0:path.index(':')] )
                path = path[ path.index(':') + 1 :]
                doc =  get_doc(path, items[left]['items'])
            else:

                path = int(path)
                item_cour = items[path]

                if item_cour.has_key('cat'):

                    if item_cour.has_key('doc'):
                        doc = item_cour['doc']
                    else:
                        # todo : faire un résumé de toute la cat ?
                        # (reuse code get_apps)
                        doc = utils.construct_doc(item_cour['items'], item_cour['cat'])

                    return doc

                if item_cour.has_key('title') and item_cour['title'] not in self.labels.keys():
                    doc = utils.construct_doc(item_cour)
                    self.labels[item_cour['title']] = doc

                else:
                    # on a déjà calculé la doc, elle est stockés dans self.labels
                    doc = self.labels[item_cour['title']]

            return doc


        model, treeiter = selection.get_selected()
        if treeiter != None:

            path = self.treeModel.get_path(treeiter).to_string()

            doc =  get_doc(path, self.ITEMS)
            # self.frame2.set_label(model[treeiter][0])
            # self.label.set_text(doc)
            self.label.set_markup(doc)

            # Afficher l'image, s'il y a :

            it_cour = self.get_item(path)
            if it_cour.has_key('im'):
                # On ne connait pas l'image :
                if not it_cour['title'] in self.images:

                    image = utils.get_img(it_cour['im'].strip() )

                    if not image:
                        print 'No image to display for %s.' % it_cour['title']
                        # It does not work, so we don't want to try each time
                        # (slows dowmn the UI)
                        it_cour.pop('im')

                        self.im.set_from_resource(None)

                        return

                    self.images[it_cour['title']] = image.strip()
                    self.im.set_from_file(image)

                else:
                    # on connait déjà l'image associée
                    self.im.set_from_file(self.images[it_cour['title']])


            else:
                # il n'y a pas d'image
                # set_from_file(None) montrera
                # une icône, la ligne suivante n'affichera rien.
                self.im.set_from_resource(None)



            return



            # item_cour = self.ITEMS[int(path) ]
            # if item_cour.has_key('cat'):
            #     #todo
            #     self.frame2.set_label(item_cour['cat'])
            #     return

            # if item_cour['title'] not in self.labels.keys():
            #     # We have to construct the documentation

            #     if item_cour.has_key('doc'):
            #         self.labels[item_cour['title']] = item_cour['doc']
            #         print 'doc= ', item_cour['doc']
            #         self.frame2.set_label(item_cour['doc'])
            #     elif item_cour.has_key('title'):
            #         self.frame2.set_label(item_cour['title'])
            #     else:
            #         self.frame2.set_label('pas de titre')



            # else:
            #     self.labels[model[treeiter][0]] = 'this is some dooooooooc'
            #     # frame.set_label(self.labels[model[treeiter][0]])
            #     self.frame2.set_label(self.labels[model[treeiter][0]])



    def on_treeview1_cursor_changed(self):
        """étude : cursor_changed fait quoi ?

        """
        print 'on_treeview1_cursor_changed'
        pass





    def on_cell_toggled(self, widget, path, renderer_toggle):
        """Méthode de callback du CellRendererToggle, quand on coche, qui détermine si la case est cochée ou dans un état inconsistent.

        Doit parcourir toute la branche du modèle concernée (donc pour une cat: tous les fils).
        """
        def propagate(iter, toggled):

            while iter:
                if  self.treeModel.get_value(iter, 0) in postinstaller.CATS:
                    propagate(self.treeModel.iter_children(iter), toggled)

                self.treeModel.set_value(iter, 1, toggled)
                iter = self.treeModel.iter_next(iter)
                #end propagate


        if self.treeModel[path][0] in postinstaller.CATS:

            iter = self.treeModel.get_iter(path)
            toggled =  not self.treeModel.get_value(iter, 1)
            self.treeModel[path][1] = not self.treeModel[path][1]

            # if inconsistent, then untoggle
            if renderer_toggle.get_property('inconsistent'):
                self.treeModel[path][1] = False
                toggled = False

            child_iter = self.treeModel.iter_children(iter)
            while child_iter:
                # if we have another nested category
                if self.treeModel.get_value(child_iter, 0) in postinstaller.CATS:
                    propagate(self.treeModel.iter_children(child_iter), toggled)

                self.treeModel.set_value(child_iter, 1, toggled)
                child_iter = self.treeModel.iter_next(child_iter)

        else:

            self.treeModel[path][1] = not self.treeModel[path][1]


    def hello(self, widget):
        print 'Hello World !'


    def on_button2_clicked(self, widget):
        Gtk.main_quit()


    def display_dialog(self, message):
        """Affiche une boite de dialogue d'information très simple pour afficher le message donné.
        """

        # boite de dialogue très rapide :
        self.dialog = self.builder.get_object('messagedialog1')
        self.dialog.format_secondary_text(message)
        self.dialog.run()
        self.dialog.hide()


        self.expander.set_label(message)


    def install_apps(self):
        # s'inspirer de mintinstall
        # https://github.com/linuxmint/mintinstall/blob/master/usr/bin/mint-synaptic-install

        #  systèmes sans synaptic : on tente de récupérer la commande
        #  d'installation du gestionnaire de paquets qu'on exécute
        #  normalement.

        #  à voir pour les autres plateformes ce qu'on peut faire avec
        #  leur installateur graphique.

        if self.TO_INSTALL:
            if os.path.isfile(_SYNAPTIC_PATH):
                ret = utils.synaptic_install(self.TO_INSTALL)

                if ret == 0:

                    self.display_dialog("Tous les paquets ont été installés avec succès.")


            else:
                pacman = utils.get_package_manager(packman=postinstaller._PACKMAN)
                if not pacman:
                    print "ERROR: what is your platform and your package manager ? Please e-mail the developper. No packages will be installed."

                else:

                    cmd = [pacman, ' '.join(['%s' % pac for pac in self.TO_INSTALL]) ]
                    comnd = Popen( ['gksudo', ' '.join(cmd)], stdout=PIPE, stderr=PIPE ) # todo: remplacer gksudo par sudocmnd
                    ret = comnd.wait()

                    # utils.exec_command("gksudo " + pacman +
                                       # " ".join( ['%s' % app for app in postinstaller.TO_INSTALL] ))

        # utils.packages_install(self.TO_INSTALL)

    # def execute_commands(self):
        ERROR = False
        for cmd in self.TO_EXEC:
            self.expander.set_label("Exécution de " + cmd)
            returnCode, stdout, stderr = utils.exec_command(cmd)
            if returnCode == 1:
                ERROR = True
                print 'erreur lors de l execution de ', cmd

        if ERROR:
            #TODO: le mieux est de récupérer la liste et d'afficher un dialogue avec expander qui montre les stderr.
            self.expander.set_label("Des commandes ont échoué")

        else:

            if len(self.TO_EXEC):
                # boite de dialogue très rapide :
                self.display_dialog("Toutes les commandes ont été exécutées avec succès.")

                # self.dialog = self.builder.get_object('messagedialog1')
                # self.dialog.format_secondary_text('Toutes les commandes ont été executées avec succès.')
                # self.dialog.run()
                # self.dialog.hide()


                # self.expander.set_label("Toutes les commandes ont été executées avec succès")


        if self.DO_UPGRADE:
            ret = utils.do_upgrade()

            if ret != 0:
                self.display_dialog("La mise à jour n'a pas pu se produire.")


    def btnValidate_clicked(self, widget):
        """Rempli les listes self.TO_INSTALL et self.TO_EXEC des
        apps et des commandes shell de tout ce qui est
        sélectionné."""

        self.TO_INSTALL = []
        self.TO_EXEC = []
        self.DO_UPGRADE = False

        def get_apps(iter_cour):
            """Parcours récursivement le treeModel à la recherche des éléments sélectionnés.

            Arguments:
            - `iter_cour`: iterateur
            """
            if self.treeModel.iter_has_child(iter_cour):
                get_apps(self.treeModel.iter_children(iter_cour))


            # si elt est cliqué
            if self.treeModel.get_value(iter_cour, 1):
                item = self.get_item(self.treeModel.get_path(iter_cour).to_string())
                if 'apps' in item.keys():
                    for app in item['apps']:
                            self.TO_INSTALL.append(app)

                elif 'sh' in item.keys():

                    # gérer l'item qui demande une upgrade
                    if item.has_key('upgrade'):
                        self.DO_UPGRADE = True

                    else:
                        for cmd in item['sh']:
                            self.TO_EXEC.append(cmd)
                else:
                    print 'ni commande, ni app pour : ', item

            # fin if elt cliqué
            # Si elt suivant, continuer, sinon return
            iter_cour = self.treeModel.iter_next(iter_cour)
            if iter_cour:
                get_apps(iter_cour)
            else:
                return



        iter_cour = self.treeModel.get_iter_first()
        get_apps(iter_cour)


        print 'Installer les paquets: ',  self.TO_INSTALL
        print 'Exec les commandes : ', self.TO_EXEC
        # from infoWindow import InfoWindow


        # infoWindow = InfoWindow(self.TO_INSTALL, self.TO_EXEC, builder=self.builder)
        # infoWindow = InfoWindow(self)
        # response = infoWindow.run()

        self.dialog = self.builder.get_object('dialog1')
        self.label = self.builder.get_object('label6')
        if not self.TO_INSTALL and not self.TO_EXEC and not self.DO_UPGRADE:
            text = "Aucun programme à installer ou de commande à exécuter. Rien à faire."
        else:

            text = ""
            if self.TO_INSTALL:
                text += "Vous avez choisi d'installer les paquets suivants :\n\n"
                text += ' '.join( ['%s' % app for app in self.TO_INSTALL] ) + "\n\n"
            if self.TO_EXEC:
                text += "Vous avez choisi d'exécuter les commandes suivantes :\n\n"
                text += '\n'.join( ['%s' % app for app in self.TO_EXEC] ) + "\n\n"

            if self.DO_UPGRADE:
                text += "Vous mettrez à jour le système.\n\n"

            text += "Souhaitez-vous continuer ?"

        self.label.set_text(text)

        resp = self.dialog.run()
        if resp == 0:
            self.dialog.hide()  # et pas destroy(), sinon on ne peut pas le rappeler.

            # on n'a pas de retour visuel pendant l'exéc, on reste sur
            # le bouton du dialogue…
            self.install_apps()
            # self.execute_commands()

        elif resp == 1:
            self.dialog.hide()


    def quit(self, widget, bar):
        """
        """
        Gtk.main_quit()



if __name__ == "__main__":

    script_name = "mint-postinstall.sh"

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if sys.argv[1].endswith('.glade'):
            GLADEFILE = sys.argv[1]

        elif arg.startswith('http'):
            script_name = utils.dl_url(arg) # TODO à tester

        else:
            script_name = sys.argv[1]

    script = open(script_name)
    PostInstaller = PostInstaller(script=script)
    Gtk.main()
