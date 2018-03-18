import unittest
import __builtin__
import src.symbian.appuifw as appuifw

from src.shopping_list import ShoppingList

class Shopping_list_tester(unittest.TestCase):
    '''The main tester'''
    
    def mock_raw_input(self, vals):
        gen = iter(vals)
        def raw(promt):  # @UnusedVariable
            return gen.next()
        __builtin__.raw_input = raw
    
    def setUp(self):
        ShoppingList.XML_DATA_FILE = '../db/test_products.xml'
        self.sut = ShoppingList()
        self.mock_raw_input(['dep1',
                             0, 'prod11',
                             0, 'prod12',
                             'dep2',
                             1, 'prod21',
                             1, 'prod22',
                             ])
        self.sut.at_addDepart()
        self.sut.at_addProduct()
        self.sut.at_addProduct()
        
        self.sut.at_addDepart()
        self.sut.at_addProduct()
        self.sut.at_addProduct()
        
    def test_test(self):
        print self.sut.products_list.lst
        print self.sut.products.getAllProducts()
        print self.sut.products.departments
        print self.sut.products.getChecked()
        print self.sut.products.getUnchecked()
        print self.sut.products.getDepartsList()
    
    def test_show_all_after_deparm(self):
        self.sut.at_mode()
        self.failIf(appuifw.app.title != u"Shopping list. Departments.")
        self.failIf(self.sut.products_list.lst[0] != u'-- All departments')
        
        self.sut.at_mode()
        self.assertEqual(appuifw.app.title, u"Shopping list")
        self.assertEqual([u'prod11', u'prod12', u'prod21', u'prod22'],
                         self.sut.products.getChecked())
        
        