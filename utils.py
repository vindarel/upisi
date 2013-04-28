#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import platform
import tempfile
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

    Arguments: - `item`: dico devant contenir 'title' et pouvant
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
    if item.has_key('doc'):
        doc = item['doc'] + "\n\n"
        doc_cour = doc.strip()

        if doc.startswith('http'): # in doc:
            doc = "Veuilez visiter le site suivant pour plus d'informations :\n"
            doc += link(doc_cour, doc_cour, doc_cour) + "\n\n"
        elif 'http' in doc:

            try:
            # Remplacer [http://foo | texte] par la syntaxe Gtk
            # il faudra trouver un outil existant.
                lien = re.findall('http.*\|', doc)
                lien = lien[0].replace("|", "")

                txt = re.findall("\|.*]", doc)
                txt = txt[0].replace("|", "")
                txt = txt.replace("]", "")
                url_txt = link(txt, lien, lien)

                all_occ = re.findall('\[.*\]', doc)
                doc = doc.replace(all_occ[0], url_txt)

            except:
                print "Error in manipulating http link for %s" % doc
                return doc


    if item.has_key('sh'):
        doc += "Cet élément lancera les commandes suivantes :"
        doc += "\n\t" + "\n\t".join( ['%s' % cmd for cmd in item['sh'] ])
        if doc.endswith('&'):
            # Gtk ne rend pas le texte s'il y a une esperluette.  Il
            # faut les échapper (remplacer & par &amp; ) et c'est
            # possible avec cgi.escape
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



def get_package_manager(packman):
    """todo: à tester !

    L'argument 'packman' est celui trouvé dans le script de
    post-install. Mais ce n'est pas forcément le bon, car upisi essaie
    de se baser sur l'installateur du système et pas sur ce qu'il y a
    écrit dans le fichier, afin de rendre des scripts plus généraux
    (qu'on puisse utiliser les recommendations données par les lignes
    'aptitude install' sous une Suse par exemple (les paquets les
    plus courants ont le même nom). C'est plus souple pour
    l'utilisateur. Voir à l'usage."""

    # existe-t-il méthode plus automatique ??
    # platform.linux_distribution() -> (LinuxMint, 1, Debian)

    plat = platform.platform()

    if 'debian' or 'ubuntu' or 'mint' or 'trisquel' or 'mepis' or 'zorin' \
            or 'solus' or 'snowlinux' or 'pinguy' or 'pureos' or 'bodhi' or 'crunchbang' in plat:
        # useful list ?
        return "apt-get install"

    elif 'sabayon' or 'gentoo' in plat:
        return "equo install"

    elif 'arch'  or 'manjaro' or 'chakra' in plat:
        return "pacman -S"

    elif 'fedora' or 'korora' in plat:
        return "yum install"

    elif 'mandriva' or 'rosa' or 'mageia' or 'mandrake' or 'pclinuxos' in plat:
        return "urpmi"

    elif 'suse' in plat:
        return "zypper install"

    else:
        if packman:
            return packman
        else:
            return None


def dl_url(url):
    """Télécharge le fichier texte désigné par l'url, crée un fichier temporaire et retourne le fichier ouvert en lecture (ou None si impossible).

    """
    if not url.startswith('http'):
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
