#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '2.1'
__author__ = 'OD'


import xml.etree.ElementTree as ET
import ConfigParser
import os, sys

SYMBIAN = True if sys.platform == 'symbian_s60' else False

if SYMBIAN:
	import e32  # @UnresolvedImport
	import appuifw  # @UnresolvedImport @UnusedImport
else:
	from symbian import appuifw # @Reimport

EMPTY_LIST_MARK = unicode('The shopping list is empty.')


class ListConfig:
	'''The class is responsible for creating default configurations,
	reading, and writing configurations. The config file has next structure:
	
	[state]
		active_list = shopping
	
	[lists]
		shopping = *path to shopping list*
		travel = *path to treval list*
	
	'''

	if SYMBIAN:
		PYTHON_DIR = 'e:\\data\\python\\'
		RESOURCES_DIR = 'resources\\list\\'
		CONFIG_FILE = 'list.cfg'
	else:
		PYTHON_DIR = '..'
		RESOURCES_DIR = '/resources/db/'
		CONFIG_FILE = '../config/list.cfg'

	@staticmethod
	def get_path_to_resources():
		return ListConfig.PYTHON_DIR + ListConfig. RESOURCES_DIR

	@staticmethod
	def get_path_to_config():
		return ListConfig.get_path_to_resources() + ListConfig.CONFIG_FILE

	def __init__(self):
		self.parser = ConfigParser.RawConfigParser()
		if len(self.parser.read(ListConfig.get_path_to_config())) == 0:
			self.__create_defult_config()
	
	def __create_defult_config(self):
		section = 'state'
		self.parser.add_section(section)
		self.parser.set(section, 'active_list', 'shopping')

		section = 'lists'
		resources = ListConfig.get_path_to_resources()
		self.parser.add_section(section)
		self.parser.set(section, 'shopping', os.path.join(resources, 'shopping_ua.xml'))
		self.parser.set(section, 'travel', os.path.join(resources, 'travel_ua.xml'))
		self.__update_file()

	def __update_file(self):
		f = open(ListConfig.get_path_to_config(), 'w')
		self.parser.write(f)
		f.close()

	def get_list_file(self):
		return self.parser.get('lists', self.get_state())

	def get_lists_names(self):
		'''returns all lists mentioned in the configuration file'''
		options = self.parser.options('lists')
		return options

	def set_state(self, state):
		self.parser.set('state', 'active_list', state)
		self.__update_file()

	def get_state(self):
		return self.parser.get('state', 'active_list')


class Listbox():
	'''Extends appyifw Listbox'''
	
	def __init__(self, init_list, cb_handler):
		self.lst = init_list if len(init_list) else [EMPTY_LIST_MARK,]
		self._ui_list = appuifw.Listbox(self.lst, cb_handler)
	
	def current_item(self):
		idx = self._ui_list.current()
		return self.lst[idx]
	
	def add_item(self, item):
		if len(self.lst) == 1 and self.lst[0] == EMPTY_LIST_MARK:
			del self.lst[0]
		self.lst.append(item)
		self._ui_list.set_list(self.lst, self._ui_list.current())
	
	def remove_item(self, item):
		self.lst.remove(item)
		if len(self.lst) == 0: #cannot set an empty list
			self.lst = [EMPTY_LIST_MARK,]
		self._ui_list.set_list(self.lst, self._ui_list.current())
		
	def set_list(self, lst):
		self.lst = lst
		cur = self._ui_list.current() if len(lst) else None
		self._ui_list.set_list(lst, cur)
		
	def cb_focus_up(self):
		pos = self._ui_list.current() - 1
		if pos < 0: pos = len(self.lst)-1
		self._ui_list.set_list(self.lst, pos)
	
	def cb_focus_down(self):
		pos = self._ui_list.current() + 1
		if pos > len(self.lst)-1: pos = 0
		self._ui_list.set_list(self.lst, pos)
	
	@property
	def ui_list(self):
		return self._ui_list


class Products:
	'''Manages products, works with xml'''
	
	def __init__(self, xml_file):
		self._xml_file = xml_file
		self._departs = self._getData()
		self.last_msg = u''
	
	def _getData(self):
		# Get a list of products.
		# Each product is a dict with a name and a flag (is in list)
		tree = ET.parse(self._xml_file)
		root = tree.getroot()
		assert root.tag == 'products', 'unknown xml'
		departs = []
		for depart in root:
			products = []
			for prod in depart:
				products.append({'name': prod.attrib['name'], 'chk': prod.attrib['inlist']})
			departs.append({'name': depart.attrib['name'], 'products': products})
		return departs
	
	def saveData(self):
		root = ET.Element('products')
		for dep in self._departs:
			d = ET.SubElement(root, 'department', {'name': dep['name']})
			for prod in dep['products']:
				ET.SubElement(d, 'product', {'inlist': prod['chk'], 'name': prod['name']})
		tree = ET.ElementTree(root)
		tree.write(self._xml_file)
	
	def departments(self):
		return [dep['name'] for dep in self._departs]
	
	def put_in_list(self, name):
		self._set_inlist_val(name, '1')
				
	def put_out_list(self, name):
		self._set_inlist_val(name, '0')
		
	def _set_inlist_val(self, name, value):
		for deps in self._departs:
			for prod in deps['products']:
				if prod['name'] == name:
					prod['chk'] = value
					return
	
	def is_product_checked(self, product):
		return product['chk'] == '1'
	
	def _products(self):
		return [prod for dep in self._departs for prod in dep['products']]
	
	def get_all_products(self):
		return [unicode(prod['name']) for dep in self._departs for prod in dep['products']]
		
	def get_checked(self):
		# return a list of names that are checked
		return [unicode(x['name']) for x in self._products() if self.is_product_checked(x)]
	
	def get_unchecked(self):
		#return a list of names that are NOT checked
		return [unicode(x['name']) for x in self._products() if not self.is_product_checked(x)]
	
	def get_departs_list(self):
		return [unicode(x['name']) for x in self._departs]
	
	def get_checked_by_dep(self, name):
		if not name:
			return self.get_checked()
		for depart in self._departs:
			if depart['name'] == name:
				return [prod['name'] for prod in depart['products']
							if self.is_product_checked(prod)]
		return []
	
	def add_product(self, name, depart_name):
		#check if the product has already been in the list
		if name in [x for x in self.get_all_products()]:
			self.last_msg = u'The product has already been in the list.'
			return 1
		else:
			#update the product list
			product = {'name': name, 'chk': '1'}
			for dep in self._departs:
				if dep['name'] == depart_name:
					dep['products'].append(product)
					return 0
			self.last_msg = u'%s not found.'%(depart_name)
			return 1
	
	def removeProduct(self, name):
		for idx in range(len(self._departs)):
			for jdx in range(len(self._departs[idx]['products'])):
				if name == self._departs[idx]['products'][jdx]['name']:
					del self._departs[idx]['products'][jdx]
					return 0
		self.last_msg = u'The product is not in the list.'
		return 1
	
	def addDepart(self, name):
		if name in [x['name'] for x in self._departs]:
			self.last_msg = u'A department with name %s has been in the list'%name
			return 1
		new_dep = {'name': name, 'products': []}
		self._departs.append(new_dep)
		return 0
	
	def removeDepart(self, name):
		if name not in [x['name'] for x in self._departs]:
			self.last_msg = u'A department with name %s is not in the list'%name
			return 1
		for idx in range(len(self._departs)):
			if self._departs[idx]['name'] == name:
				del self._departs[idx]
				return 0
		return 1


class ShoppingList:
	''' Shopping list 
	Select products to buy in 'At home' menu.
	Show selected products by departments in 'By departments'.
	In 'Modify the list' add or remove a product or department.
	In main menu 2 and 8 are navigation keys, 5 - select.
	'''
	
	TITLE = u"The list."

	def __init__(self):
		appuifw.app.title = ShoppingList.TITLE
		appuifw.app.screen = "normal"
		
		self.config = ListConfig()
		self._load_products_to_the_list()
		self.products_list.ui_list.bind(0x35, self.products_list_handler) #bind the handler to key 5
		self.products_list.ui_list.bind(0x32, self.products_list.cb_focus_up) #bind the handler to key 2
		self.products_list.ui_list.bind(0x38, self.products_list.cb_focus_down) #bind the handler to key 8
		
		#an experiment with C and pancil
		self.products_list.ui_list.bind(0x8, self.at_removeProduct) #C key
		#WARNING: don't use pencil because the button starts its own menu right after dialog open
		#self.products_list.ui_list.bind(0xf80b, self.at_addProduct) # pencil key
		self.products_list.ui_list.bind(0x2a, self.at_addProduct) # * key
	
		appuifw.app.exit_key_handler = self.quit
		appuifw.app.menu = [
							(u'At home', self.at_home),
							(u'By departments', self.at_mode), # this position is fixed!
							(u'Modify the list', self.at_list_manager),
							(u'Select list', self.at_select_list),
							(u'Info', self.about),
							]
		self.product_mode = True

		#next two lines lock the main thread, so they should be at the end of __init__ when everything has been created.
		if SYMBIAN:
			self.script_lock = e32.Ao_lock()
			self.script_lock.wait()
		
	def at_list_manager(self):
		menu_items = [u'Add product',
					u'Remove product',
					u'Add departament',
					u'Remove departament']
		menu_item_foo = [self.at_addProduct,
						self.at_removeProduct,
						self.at_addDepart,
						self.at_removeDepart]
		idx = appuifw.popup_menu(menu_items)
		if not idx == None:
			menu_item_foo[idx]()

	def at_mode(self):
		if self.product_mode:
			appuifw.app.title = appuifw.app.title + u" Departments." 
			appuifw.app.menu[1] = (u'All goods', self.at_mode)
			self.products_list.set_list([u'-- All departments',] + self.products.get_departs_list())
			self.product_mode = False
		else:
			#'all goods' selected
			appuifw.app.title = self.__compose_the_title()
			appuifw.app.menu[1] = (u'By departments', self.at_mode)
			self.products_list.set_list(self.products.get_checked())
			self.product_mode = True

	def at_select_list(self):
		menu_items = [unicode(x) for x in self.config.get_lists_names()]
		idx = appuifw.popup_menu(menu_items)
		if idx is not None:
			self.config.set_state(menu_items[idx])
			self._load_products_to_the_list()

	def _removeDepName(self, full_name):
		#full name means product: department
		pos = full_name.find(u':')
		if pos > 0:
			name = full_name[:pos]
		else:
			name = full_name
		return name

	def _load_products_to_the_list(self):
		self.products = Products(self.config.get_list_file())
		
		self.products_list = Listbox(self.products.get_checked(), self.products_list_handler)
		appuifw.app.body = self.products_list.ui_list
		appuifw.app.title = self.__compose_the_title()

	def __compose_the_title(self):
		return u"%s %s"%(ShoppingList.TITLE, self.config.get_state().title())
	
	def products_list_handler(self):
		name = self.products_list.current_item()
		if self.product_mode:
			#remove department name
			if name != EMPTY_LIST_MARK:
				self.products.put_out_list(self._removeDepName(name))
				self.products_list.remove_item(name)
		else:
			lst = self.products.get_checked_by_dep(name if not name.startswith(u'--') else None)
			self.products_list.set_list(lst if len(lst) else [EMPTY_LIST_MARK,])
			appuifw.app.menu[1] = (u'By departments', self.at_mode)
			appuifw.app.title = self.__compose_the_title() + u'. ' + name
			self.product_mode = True
		
	def run(self):
		pass
	
	def at_home(self):
		appuifw.app.title = u"At home. Select goods."
		unchecked = self.products.get_unchecked()
		if len(unchecked) == 0:
			appuifw.note(u"Everything has been added to the list.", "info")
		else:
			idxs = appuifw.multi_selection_list(unchecked, style='checkbox', search_field=1)
			for idx in idxs:
				self.products.put_in_list(unchecked[idx])
			self.products_list.set_list(self.products.get_checked())

		#switch mode to product
		self.product_mode = False
		self.at_mode()
	
	def at_addProduct(self):
		appuifw.app.title = u'Add a new item. Select a department.'
		departs = self.products.get_departs_list()
		idx = appuifw.selection_list(departs, search_field=1)
		if not idx == None:
			depart_name = departs[idx]
			appuifw.app.title = u'Add a new item.'
			prod_name = appuifw.query(u'Enter an item name.', 'text')
			if prod_name and not u':' in prod_name: # : used to separate product name and department in 'by depart' mode
				if not prod_name.lower() in self.products.get_all_products():
					if self.products.add_product(prod_name.lower(), depart_name):#return 1 - cannot add, otherwise - 0
						appuifw.note(u"Cannot add the item.\n%s"%self.products.last_msg, "error")
					else:
						self.products_list.add_item(prod_name.lower())
				else:
					appuifw.note(u'%s has been at the list.'%prod_name.lower(), "error")
			else:
				pass # 'cancel' was presssed on product name
		else:
			pass # 'cancel' was pressed on department name
		appuifw.app.title = ShoppingList.TITLE
		
	def at_removeProduct(self):
		appuifw.app.title = u'Remove goods. Select a department.'
		lst = self.products.get_all_products()
		idx = appuifw.selection_list(lst, search_field=1)
		if not idx == None:
			prod_name = lst[idx]
			if appuifw.query(u"Remove %s?"%prod_name, "query") == 1:
				self.products.removeProduct(prod_name)
				self.products_list.remove_item(prod_name)
		appuifw.app.title = ShoppingList.TITLE
		
	def at_addDepart(self):
		appuifw.app.title = u'Add a new department.'
		depart_name = appuifw.query(u'Add a depart name.', 'text')
		if depart_name:
			if self.products.addDepart(depart_name):
				appuifw.note(u'%s'%self.products.last_msg, 'error')
		appuifw.app.title = ShoppingList.TITLE
		appuifw.note(u'%s added.'%depart_name, 'info')
	
	def at_removeDepart(self):
		appuifw.app.title = u'Remove a department.'
		lst = self.products.get_departs_list()
		idx = appuifw.selection_list(lst, search_field=1)
		if not idx == None:
			depart_name = lst[idx]
			if appuifw.query(u"Remove %s?"%depart_name, "query") == 1:
				if self.products.removeDepart(depart_name):
					appuifw.note(u"%s"%self.products.last_msg, "error")
		appuifw.app.title = ShoppingList.TITLE
					
	def about(self):
		appuifw.note(u'The list v.%s'%__version__,
					"info")

	def quit(self):
		self.products.saveData()
		appuifw.app.exit_key_handler = None
		if SYMBIAN:
			self.script_lock.signal()


if __name__ == '__main__':
	ShoppingList().run()
