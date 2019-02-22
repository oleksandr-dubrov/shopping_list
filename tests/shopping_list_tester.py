#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __builtin__
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('../src'))

import symbian.appuifw as appuifw
from shopping_list import ShoppingList


class Shopping_list_tester(unittest.TestCase):
    '''The main tester'''

    # specify a path to xml; it should be the same as in list.cfg
    XML = [os.path.join('test_shopping.xml'),
           os.path.join('test_travel.xml')]

    def mock_raw_input(self, vals):
        gen = iter(vals)

        def raw(promt):  # @UnusedVariable
            return gen.next()
        __builtin__.raw_input = raw

    def resetXml(self, paths):
        for p in paths:
            with open(p, 'w') as f:
                f.write('<products></products>')

    def setUp(self):
        self.resetXml(Shopping_list_tester.XML)
        self.sut = ShoppingList()
        self.mock_raw_input(['dep1',
                             0, 'prod11',
                             0, 'prod12',
                             'dep2',
                             1, 'prod21',
                             1, 'prod22',
                             'trev_dep1',
                             0, 'trev_prod21',
                             1, 'trev_prod22',               
        ])
        self.sut.at_add_depart()
        self.sut.at_add_product()
        self.sut.at_add_product()

        self.sut.at_add_depart()
        self.sut.at_add_product()
        self.sut.at_add_product()

        self.sut.config.set_state('travel')
        self.sut.products.save_data()
        self.sut._load_products_to_the_list()

        self.sut.at_add_depart()
        self.sut.at_add_product()
        self.sut.at_add_product()

        self.sut.config.set_state('shopping')
        self.sut.products.save_data()
        self.sut._load_products_to_the_list()

    def tearDown(self):
        for p in Shopping_list_tester.XML:
            if os.path.isfile(p):
                os.remove(p)

    def test_test(self):
        '''base test case'''
        self.sut.products_list.lst
        self.sut.products.get_all_products()
        self.sut.products.departments
        self.sut.products.get_checked()
        self.sut.products.get_unchecked()
        self.sut.products.get_departs_list()

    def test_show_all_after_depart(self):
        self.sut.at_mode()
        self.assertEqual(appuifw.app.title, u"The list. Shopping Departments.")
        self.failIf(self.sut.products_list.lst[0] != u'-- All departments')

        self.sut.at_mode()
        self.assertEqual(appuifw.app.title, u"The list. Shopping")
        self.assertEqual([u'prod11', u'prod12', u'prod21', u'prod22'],
                         self.sut.products.get_checked())

    def test_add_the_product_twice(self):
        ''' add the stdout verification if you want '''
        self.mock_raw_input([0, 'prod11'])
        self.sut.at_add_product()

    def test_remove_product(self):
        self.mock_raw_input(['2', 'prod21'])
        self.sut.at_remove_product()
        self.assertEqual([u'prod11', u'prod12', u'prod22'],
                         self.sut.products.get_checked())

    def test_remove_depart_with_prod(self):
        self.mock_raw_input([0, '1', 'prod21'])
        self.sut.at_remove_depart()
        self.assertEqual([u'prod21', u'prod22'],
                         self.sut.products.get_checked())

    def test_save_data(self):
        self.sut.quit()

    def test_put_in_out_list(self):
        self.sut.products.put_out_list('prod22')
        self.sut.products.put_in_list('prod22')
        self.assertEqual([u'prod11', u'prod12', u'prod21', u'prod22'],
                         self.sut.products.get_checked())


if __name__ == "__main__":
    unittest.main()
