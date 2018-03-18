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
    
    def resetXml(self):
        with open(ShoppingList.JSON_DATA_FILE, 'w') as f:
            f.write('<products></products>')
        
    def setUp(self):
        ShoppingList.JSON_DATA_FILE = '../db/test_products.xml'
        self.resetXml()
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
        print self.sut.products.get_all_products()
        print self.sut.products.departments
        print self.sut.products.get_checked()
        print self.sut.products.get_unchecked()
        print self.sut.products.get_departs_list()
    
    def test_show_all_after_depart(self):
        self.sut.at_mode()
        self.failIf(appuifw.app.title != u"Shopping list. Departments.")
        self.failIf(self.sut.products_list.lst[0] != u'-- All departments')
        
        self.sut.at_mode()
        self.assertEqual(appuifw.app.title, u"Shopping list")
        self.assertEqual([u'prod11', u'prod12', u'prod21', u'prod22'],
                         self.sut.products.get_checked())
    
    def  test_add_the_product_twice(self):
        ''' add the stdout verification if you want '''
        self.mock_raw_input([0, 'prod11'])
        self.sut.at_addProduct()
    
    def test_remove_product(self):
        self.mock_raw_input(['2', 'prod21'])
        self.sut.at_removeProduct()
        self.assertEqual([u'prod11', u'prod12', u'prod22'],
                         self.sut.products.get_checked())
    
    def test_remove_depart_with_prod(self):
        self.mock_raw_input([0, '1', 'prod21'])
        self.sut.at_removeDepart()
        self.assertEqual([u'prod21', u'prod22'],
                         self.sut.products.get_checked())
    
    def test_save_data(self):
        self.sut.quit()
    
    def test_put_in_out_list(self):
        self.sut.products.put_out_list('prod22')
        self.sut.products.put_in_list('prod22')
        self.assertEqual([u'prod11', u'prod12', u'prod21', u'prod22'],
                         self.sut.products.get_checked())