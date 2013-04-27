#! /usr/bin/python
# -*- coding: utf-8 -*-

# utiliser env-init.sh dans test/ pour bien mettre le pythonpath
#export PYTHONPATH=${PYTHONPATH}:/home/vince/projets/postinstaller
import postinstaller

import unittest


"""Tests du parser"""
# Pas le choix, il faut accéder très précisément aux listes,
# tant qu'on n'est pas en pur OO.
# Utiliser postinstaller.printitems(items) pour y voir plus clair.

class TestParser(unittest.TestCase):


    def setUp(self):
        pass


    def test_documentation(self):
        """Lis la documentation inscrite sur plusieurs lignes, prend en
        compte le tag _GUI.
        """
        # passer autre chose que des fichiers ?
        script = open('data_doc.sh', 'r')

        items = postinstaller.main(script)
        # postinstaller.printitems(items)

        self.assertTrue(len(items), 4)
        self.assertTrue('super' in items[0]['doc'] )
        self.assertTrue('intéressant' in items[0]['doc'] )


        self.assertTrue('toggle' not in items[0]['doc'], "la ligne gui:toggle qui vient juste après une doc sur plusieurs lignes est comptée dans la doc." )

        self.assertTrue('image.jpg' not in items[0]['doc'], "le lien de l'image qui vient juste après une doc sur plusieurs lignes est comptée dans la doc." )

        self.assertTrue('secret' not in items[0]['doc'], "une ligne de commentaire qui vient juste après une doc sur plusieurs lignes est comptée dans la doc." )



        self.assertEqual(items[0]['gui_toggle'], False, 'il faut prendre en compte le toggle')
        self.assertEqual(items[1]['gui_toggle'], True, "mauvaise prise en compte de toggle")


    def test_categories(self):
        """
        Deux cat imbriquées.
        """
        script = open('data_cat.sh', 'r')
        items = postinstaller.main(script)
        # postinstaller.printitems(items)

        self.assertEqual(len(items), 3, "nombre d'éléments de items")
        self.assertEqual(len(items[1]['items']), 3, "nombre d'éléments de la cat incorrect")
        self.assertEqual(len(items[1]['items'][1]['items']), 1, "nombre d'éléments de la sous-cat")
        self.assertTrue("catégories" in items[1]['items'][-1]['doc'], "lecture de la doc sur plusieurs lignes")

    def test_to_install(self):
        """Tous les paquets à installer sont-ils pris en compte ?"""

        script = open('data_test_script.sh', 'r')
        items = postinstaller.main(script)

        # postinstaller.printitems(items)

        # self.assertEqual(len(postinstaller.TO_INSTALL), 32 , "nombre de paquets récupérés pour le package manager incorrect")




    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
