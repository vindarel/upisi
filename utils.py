#! /usr/bin/python
# -*- coding: utf-8 -*-

import postinstaller

import sys
import os
import re
import platform
import tempfile
import glob
import traceback

from cgi import escape
import subprocess #pour gksudo
from subprocess import Popen, PIPE
from os import environ

_APT_INSTALL = "DEBIAN_FRONTEND=noninteractive  apt-get -y -f install "
# _APT_INSTALL = "DEBIAN_FRONTEND=noninteractive gksudo apt-get -y -f install " #gksudo ne s'utilise pas comme ça.


def bold_str(foo):
    return '<b>'+foo+'</b>'

def link(string, mouse, url):
    # mouse : en survolant avec la souris
    # string : ce qui est cliquable
    return "<a href=\""+url+"\" title=\""+mouse+"\">"+string+"</a>"

def construct_doc(item, cat=None):
    """Construit la documentation associée à un item.

    Attention, le lien doit être de la forme [http… | txt ]

    Arguments:

    - `item`: dico devant contenir 'title' et pouvant
    contenir 'app' avec une liste de paquets à être installés, 'sh'
    avec une liste de commandes shell, 'doc'.  'doc' peut être une
    suite de str ou la référence à un site internet ou à un fichier
    local.

    - 'cat' : le titre de la cat et donc item: sa liste de dicos d'items.
    """


    if cat:
        doc = cat
        # est-ce qu'on donne un résumé de tout ce qui est coché ?

        return doc
    doc = ""



    if item.has_key('doc') and item['doc']:
        doc = item['doc'] + "\n\n"
        doc_cour = doc.strip()


    if item.has_key('sh'):

        doc += "Cet élément lancera les commandes suivantes :"
        doc += "\n\t" + "\n\t".join( ['%s' % cmd for cmd in item['sh'] ])

        # Échapper les caractères spéciaux qui font cracher Gtk, tels
        # que l'esperluette & (du coup il faut construire le lien
        # hypertexte à la fin, sinon il est aussi transformé en simple
        # texte)
        doc = escape(doc)

    elif item.has_key('apps'):
        apps = '\n\t' + '\n\t'.join( ['%s' % app for app in item['apps'] ])
        doc += bold_str('Cet élément installera les logiciels suivants :') + '\n' + apps
    elif item.has_key('title'):
        doc = item['title']
    elif item.has_key('cat'):
        doc = item['cat'] + ' on a une cat -> réc !'

    else:
        doc = 'pas de titre = pb'


    # Construire lien http :
    if doc.startswith('http'): # in doc:
        doc = "Veuilez visiter le site suivant pour plus d'informations :\n"
        doc += link(doc_cour, doc_cour, doc_cour) + "\n\n"
    elif 'http' in doc and '[' in doc: # todo: mieux reconnaître le lien«

        try:
            # Remplacer [http://foo | texte] par la syntaxe Gtk
            # il faudra trouver un outil existant.

            #  On n'a pas besoin du | au milieu !
            lien = re.findall('http.*\|', doc)
            lien = lien[0].replace("|", "")

            txt = re.findall("\|.*]", doc)
            txt = txt[0].replace("|", "")
            txt = txt.replace("]", "")
            url_txt = link(txt, lien, lien)

            all_occ = re.findall('\[.*\]', doc)
            doc = doc.replace(all_occ[0], url_txt)

        except Exception, e:
            print "Error in manipulating http link for %s. We didn't have the right syntax." % doc
            print e
            return doc



    return doc

def synaptic_install(packages): #marche pareil.
    """
    Essai d'appel à usr/bin/upisi-synaptic_install avec gksu.

    - `packages`: liste de paquets à installer.

    Retourne le code de retour de synaptic.
    """
    command = "gksu usr/bin/upisi-synaptic-install "
    for pack in packages:
        command += " " + pack


    ret = os.system(command)
    print 'code retour synaptic: ', ret
    return ret

def synaptic_install_marche(packages):
    """Installer les paquets avec l'aide de synaptic. """

    cmd = ["/usr/sbin/synaptic", "--hide-main-window", "--non-interactive"]

    f = tempfile.NamedTemporaryFile()
    print "debug attention, packages = htop"; packages = ['htop'] #debug
    for package in packages:
        f.write("%s\tinstall\n" % package)

    cmd.append("--set-selections-file")
    cmd.append("%s" % f.name)
    f.flush()

    DESKTOP_SESSION = environ.get('DESKTOP_SESSION')
    if 'kde' in DESKTOP_SESSION:
        sudocmd = 'kdesudo'
    elif DESKTOP_SESSION == 'mate' or 'gnome' in DESKTOP_SESSION:
        sudocmd = 'gksudo'
    else:
        #else I don't knom. Let's try gksudo
        print "You're not running either kde, mate or gnome. Do you have gksudo ?"
        sudocmd = 'gksudo'

    # essai avec gksudo : ok quand le logiciel est vraiment à installer.
    comnd = Popen( [sudocmd, ' '.join(cmd)], stdout=PIPE, stderr=PIPE )

    # todo: récupérer erreur quand logiciel n'existe pas ou déjà présent. Pour l'instant on ne voit rien.
    # todo: utiliser kdesudo si KDE

    # Un fichier executé en tant que root :
    # subprocess.call( ['gksudo', 'python to_exec.py'] ) #on ne voit rien

    returnCode = comnd.wait()
    print 'return code: ', returnCode #debug
    # stdout = comnd.stdout.read()
    # stderr = comnd.stderr.read()
    f.close()


def exec_command(com):
    """Exécute la commande donnée, avec les droits root avec gksudo/kdesudo si
    elle commence par sudo.
    """

    DESKTOP_SESSION = environ.get('DESKTOP_SESSION')
    if 'kde' in DESKTOP_SESSION:
        sudocmd = 'kdesudo'
    elif DESKTOP_SESSION == 'mate' or 'gnome' in DESKTOP_SESSION:
        # if not os.path.isfile('/usr/bin/gksudo'):
            # pass
        sudocmd = 'gksudo'
    else:
        #else I don't know. Let's try gksudo
        sudocmd = 'gksudo'

    if com.startswith('sudo'):#TODO
        # on obtient le bug suivant, connu depuis 2009 :
        # (gksudo:8361): GLib-CRITICAL **: g_str_has_prefix: assertion `str != NULL' failed
        # donc si on ne peut pas lancer de commandes sudo… gksudo au lancement ?
        com = com[4:]

        com = 'gksudo ' + com
        os.system(com)
        return


    else:
        print 'exec sans sudo'  # debug
        letsgo = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # letsgo = subprocess.Popen('echo salut le monde', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        returnCode = letsgo.wait()
        stdout =  letsgo.stdout.read()
        stderr =  letsgo.stderr.read()
        print 'returnCode: ', returnCode
        print 'stdout: ', stdout
        print 'stderr: ', stderr

    return (returnCode, stdout, stderr)


def do_upgrade():

    up_manager, args = get_upgrade_manager()

    if not up_manager:
        # print "Pas de gui pour upgrade. Appel système : %s" % postinstaller.UPGRADE_CMD
        print "Pas de gui pour upgrade. Appel système : quelle commande ?"
        return os.system(postinstaller.UPGRADE_CMD)


    # à factoriser ! TODO
    DESKTOP_SESSION = environ.get('DESKTOP_SESSION')
    if 'kde' in DESKTOP_SESSION:
        sudocmd = 'kdesudo'
    elif DESKTOP_SESSION == 'mate' or 'gnome' in DESKTOP_SESSION:
        sudocmd = 'gksudo'
    else:
        #else I don't knom. Let's try gksudo
        print "You're not running either kde, mate or gnome. We assume you have gksudo."
        sudocmd = 'gksudo'


    # try:
    comm = [up_manager, args]
    while "" in comm:
        comm.remove("")         # if we have no "upgrade" arguments, like with rigo, and it does bug with a ""

    cmd = Popen( [sudocmd, " ".join(comm) ] )

        # comnd = Popen( [sudocmd, ' '.join(cmd)], stdout=PIPE, stderr=PIPE )


    ret = cmd.wait()
    print 'upgrade : on retourne', ret # debug
    return ret
    # except Exception, e:
        # print e
        # traceback.print_stack()
        # return -1



def get_upgrade_manager():
   """Retourne un tuple chemin de gestionnaire de mises à jour,
   arguments de la ldc qui vont avec.
   """

   managers = {'/usr/bin/mintupdate':"",
               '/usr/bin/update-manager':"--dist-upgrade",
               '/usr/sbin/update-manager':"--dist-upgrade",
               '/usr/bin/rigo': "" }  # todo à compléter
   for manager in managers.keys():
       if os.path.isfile(manager):
           return (manager, managers[manager])

   return (None, None)

def get_package_manager(packman=None, upgrade=False):
    """todo: à tester !

    L'argument 'packman' est celui trouvé dans le script de
    post-install. Mais ce n'est pas forcément le bon, car upisi essaie
    de se baser sur l'installateur du système et pas sur ce qu'il y a
    écrit dans le fichier, afin de rendre des scripts plus généraux
    (qu'on puisse utiliser les recommendations données par les lignes
    'aptitude install' sous une Suse par exemple (les paquets les
    plus courants ont le même nom). C'est plus souple pour
    l'utilisateur. Voir à l'usage.


    - upgrade: si on veut récupérer la gui (si elle existe) pour mettre à jour le système.

    """

    # existe-t-il méthode plus automatique ??
    # platform.linux_distribution() -> (LinuxMint, 1, Debian)

    plat = platform.platform()

    def is_in_platform(alist):

        for elt in alist:
            if elt in plat:
                return True

        return False



    # if 'debian' or 'ubuntu' or 'mint' or 'trisquel' or 'mepis' or 'zorin' \
    if is_in_platform( [ 'debian', 'ubuntu' , 'mint' , 'trisquel' , 'mepis' , \
                         'zorin', 'solus' , 'snowlinux' , 'pinguy' , 'pureos',\
                         'bodhi' , 'crunchbang' ]):
        return "apt-get install"

    elif 'sabayon' in plat:
        if upgrade:
            return "rigo"
        return "rigo --install"

    elif 'gentoo' in plat:

        # or 'gentoo' in plat:
        return "equo install"

    # elif 'arch'  or 'manjaro' or 'chakra' in plat:
    elif  is_in_platform( ['arch'  , 'manjaro' , 'chakra']):
        return "pacman -S"

    # elif 'fedora' or 'korora' in plat:
    elif is_in_platform( ['fedora', 'korora'] ):
        return "yum install"

    # elif 'mandriva' or 'rosa' or 'mageia' or 'mandrake' or 'pclinuxos' in plat:
    elif is_in_platform( [ 'mandriva' , 'rosa' , 'mageia' , 'mandrake' , \
                           'pclinuxos']):
        return "urpmi"

    elif 'suse' in plat:
        return "zypper install"

    else:
        if packman:
            return packman
        else:
            return None


def dl_url(url):
    """Télécharge le fichier texte ou le dépôt git désigné par l'url, crée un fichier temporaire.

    return: le nom du fichier script, ouvert en lecture (ou None si impossible).

    """
    if not url.startswith('http'):
        print "Ceci n'est pas une url valide %s" % url
        return None

    if url.endswith('git'):
        try:
            tmp_folder = "/tmp/upisi"
            if not os.path.isdir(tmp_folder): # TODO set global variable for dir
                os.system('mkdir ' + tmp_folder)

            # on doit choper le nom du depot :
            folder_name = url.split("/")[-1][:-4] # le -4 enlève le '.git' du nom. On peut faire plus clair !

            ret = 0
            if not os.path.isdir(os.path.join(tmp_folder,folder_name)):
                cmd = "cd " + tmp_folder + "/" + " && git clone " + url
                ret = os.system(cmd)

            if ret:
                print "error while cloning git repo " + url
                return None

            # On doit trouver un script shell:
            script_list = glob.glob(os.path.join(tmp_folder,folder_name) + '/*.sh')
            if script_list:
                script_name = script_list[0]

            else:
                print "We didn't find any shell script in %s " % folder_name
                return None

            print 'on ouvre %s' % script_name
            return script_name


        except Exception, e:
            print 'Impossible de télécharger le dépôt git dans le dossier temporaire'
            print e
            return None


    # On télécharge dans un fichier temporaire.
    # On pourra faire une meilleure gestion.
    newfile = tempfile.NamedTemporaryFile()
    os.system('wget %s -O %s' % (url, newfile.name) )

    return newfile

def get_img(uri):
    """Retourne le nom du fichier de l'image. Peut être local ou téléchargé et stocké dans un fichier temporaire.
    return : str
    TODO: sauvegarde ?
    """

    if not uri.startswith('http'):
        if os.path.isfile(uri):
            return uri
        else:
            print uri + " n'est pas un fichier valide."


    else:
        imgfile = tempfile.NamedTemporaryFile()
        print 'on télécharge %s…' % uri  # debug
        ret = os.system('wget %s -O %s' % (uri, imgfile.name) )
        if not ret:             # error code is 0, which is OK
            return imgfile.name


    return None
