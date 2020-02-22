#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '2.5'
__author__ = 'OD'
__license__ = 'MIT'


import ConfigParser
import os
import xml.etree.ElementTree as ET

import e32  # @UnresolvedImport
import appuifw  # @UnresolvedImport @UnusedImport


EMPTY_LIST_MARK = unicode('The list is empty.')


class ListConfig:
	'''The class is responsible for creating default configurations,
	reading, and writing configurations.
	The configuration file has next structure:

	[state]
		active_list = shopping

	[lists]
		shopping = *path to shopping list*
		travel = *path to travel list*

	'''

	PYTHON_DIR = 'e:\\data\\python\\'
	RESOURCES_DIR = 'resources\\list\\'
	CONFIG_FILE = 'list.cfg'

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
	'''Extends appuifw Listbox'''

	def __init__(self, init_list, cb_handler):
		self.lst = init_list if len(init_list) else [EMPTY_LIST_MARK, ]
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
		if len(self.lst) == 0:  # cannot set an empty list
			self.lst = [EMPTY_LIST_MARK, ]
		self._ui_list.set_list(self.lst, self._ui_list.current())

	def set_list(self, lst):
		self.lst = lst if len(lst) else [EMPTY_LIST_MARK, ]
		self._ui_list.set_list(self.lst, self._ui_list.current())

	def cb_focus_up(self):
		pos = self._ui_list.current() - 1
		if pos < 0:
			pos = len(self.lst) - 1
		self._ui_list.set_list(self.lst, pos)

	def cb_focus_down(self):
		pos = self._ui_list.current() + 1
		if pos > len(self.lst) - 1:
			pos = 0
		self._ui_list.set_list(self.lst, pos)

	def cb_move_up(self):
		pos = self._ui_list.current()
		if not pos == 0:
			t = self.lst[pos]
			del self.lst[pos]
			self.lst.insert(pos-1, t)
			self._ui_list.set_list(self.lst, pos-1)

	def cb_move_down(self):
		pos = self._ui_list.current()
		if not pos == len(self.lst) - 1:
			t = self.lst[pos]
			del self.lst[pos]
			self.lst.insert(pos+1, t)
			self._ui_list.set_list(self.lst, pos+1)

	@property
	def ui_list(self):
		return self._ui_list


class Products:
	'''Manages products, works with xml'''

	HEADER = '<?xml version="1.0" encoding="utf-8"?><products></products>'
	DEP_WITH_CHECKED_MARKER = u'* '
	ALL_DEPARTMENTS = u'-- All departments'

	def __init__(self, xml_file):
		self._xml_file = self._make_sure(xml_file)
		self._departs = self._get_data()
		self.last_msg = u''

	def _make_sure(self, filepath):
		'''if the given filepath is not a file, create one with the XML header.'''
		if not (os.path.exists(filepath) and os.path.isfile(filepath)):
			f = open(filepath, 'w')
			f.write(Products.HEADER)
			f.close()
		return filepath

	def _get_data(self):
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

	def save_data(self):
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
		# return a list of names that are NOT checked
		return [unicode(x['name']) for x in self._products() if not self.is_product_checked(x)]

	def get_departs_list(self):
		''' get list of departments, mark departments with checked products'''
		to_be_marked = self._get_departs_list_with_checked_prods()
		all_deps = [unicode(x['name']) for x in self._departs]
		for x in range(len(all_deps)):
			if all_deps[x] in to_be_marked:
				all_deps[x] = Products.DEP_WITH_CHECKED_MARKER + all_deps[x]
		return all_deps

	def _get_departs_list_with_checked_prods(self):
		ret = []
		for d in self._departs:
			for p in d['products']:
				if p['chk'] == '1':
					ret.append(d['name'])
					break
		return ret

	def get_checked_by_dep(self, name):
		name = self._udecorate_item(name)
		if not name:
			return self.get_checked()
		for depart in self._departs:
			if depart['name'] == name:
				return [prod['name'] for prod in depart['products']
						if self.is_product_checked(prod)]
		return []

	def add_product(self, name, depart_name):
		# check if the product has already been in the list
		if name in [x for x in self.get_all_products()]:
			self.last_msg = u'The product has already been in the list.'
			return 1
		else:
			# update the product list
			product = {'name': name, 'chk': '1'}
			for dep in self._departs:
				if dep['name'] == depart_name:
					dep['products'].append(product)
					return 0
			self.last_msg = u'%s not found.' % (depart_name)
			return 1

	def remove_product(self, name):
		for idx in range(len(self._departs)):
			for jdx in range(len(self._departs[idx]['products'])):
				if name == self._departs[idx]['products'][jdx]['name']:
					del self._departs[idx]['products'][jdx]
					return 0
		self.last_msg = u'The product is not in the list.'
		return 1

	def add_depart(self, name):
		if name in [x['name'] for x in self._departs]:
			self.last_msg = u'A department with name %s has been in the list' % name
			return 1
		if name.startswith(Products.DEP_WITH_CHECKED_MARKER):
			self.last_msg = u'Invalid department name %s' % name
			return 1
		new_dep = {'name': name, 'products': []}
		self._departs.append(new_dep)
		return 0

	def remove_depart(self, name):
		name = self._udecorate_item(name)
		if name not in [x['name'] for x in self._departs]:
			self.last_msg = u'A department with name %s is not in the list' % name
			return 1
		for idx in range(len(self._departs)):
			if self._departs[idx]['name'] == name:
				del self._departs[idx]
				return 0
		return 1

	def _udecorate_item(self, i):
		if i.startswith(Products.DEP_WITH_CHECKED_MARKER):
			return i[len(Products.DEP_WITH_CHECKED_MARKER): ]
		elif not i.startswith(u'--'):
			return i
		return None

	def _undecorate_list(self, lst):
		'''remove markers from each item'''
		new_lst = []
		for l in lst:
			l = self._udecorate_item(l)
			if l:
				new_lst.append(l)
		return new_lst

	def sync_departments_order(self, lst):
		assert len(lst) == len(self._departs) + 1, 'It seems lst is not departments'
		lst = self._undecorate_list(lst)
		new_departs = []
		for x in lst:
			for y in self._departs:
				if y['name'] == x:
					new_departs.append(y)
		self._departs = new_departs
	
	def is_departments_in_list(self, lst):
		return Products.ALL_DEPARTMENTS in lst


class ShoppingList:
	''' Shopping list
	Select products to buy in 'At home' menu.
	Show selected products by departments in 'By departments'.
	In 'Modify the list' add or remove a product or department.
	In main menu 2 and 8 are navigation keys, 5 - select.

	You can select among travel or shopping list.
	'''

	TITLE = u"The list."
	BY_DEPARTMENTS = u'By departments'

	def __init__(self):
		appuifw.app.title = ShoppingList.TITLE
		appuifw.app.screen = "normal"

		self.config = ListConfig()
		self._load_products_to_the_list()

		self.products_list.ui_list.bind(0x8, self.at_remove_product)  # C key
		# WARNING: don't use pencil because the button starts its own menu right after dialog open
		# self.products_list.ui_list.bind(0xf80b, self.at_add_product) # pencil key
		self.products_list.ui_list.bind(0x2a, self.at_add_product)  # * key
		self.products_list.ui_list.bind(0x30, self.at_mode)

		appuifw.app.exit_key_handler = self.quit
		appuifw.app.menu = [
							(u'At home', self.at_home),
							(ShoppingList.BY_DEPARTMENTS, self.at_mode),  # this position is fixed!
							(u'Modify the list', self.at_list_manager),
							(u'Select list', self.at_select_list),
							(u'Help', self.at_help),
							(u'Info', self.about),
						]
		self.product_mode = True

		# next two lines lock the main thread, so they should be at the end
		# of __init__ when everything has been created.
		self.script_lock = e32.Ao_lock()
		self.script_lock.wait()

	def at_list_manager(self):
		menu_items = [u'Add product',
						u'Remove product',
						u'Add departament',
						u'Remove departament']
		menu_item_foo = [self.at_add_product,
							self.at_remove_product,
							self.at_add_depart,
							self.at_remove_depart]
		idx = appuifw.popup_menu(menu_items)
		if not idx == None:
			menu_item_foo[idx]()

	def at_mode(self):
		if self.product_mode:
			appuifw.app.title = appuifw.app.title + u" Departments."
			appuifw.app.menu[1] = (u'All goods', self.at_mode)
			all_deps = self.products.get_departs_list()
			self.products_list.set_list([Products.ALL_DEPARTMENTS, ] + all_deps)
			self.product_mode = False
		else:
			# 'all goods' selected or return from home
			if len(self.products_list.lst) \
				and self.products.is_departments_in_list(self.products_list.lst):
					self.products.sync_departments_order(self.products_list.lst)
			appuifw.app.title = self.__compose_the_title()
			appuifw.app.menu[1] = (ShoppingList.BY_DEPARTMENTS, self.at_mode)
			self.products_list.set_list(self.products.get_checked())
			self.product_mode = True

	def at_select_list(self):
		menu_items = [unicode(x) for x in self.config.get_lists_names()]
		idx = appuifw.popup_menu(menu_items)
		if idx is not None:
			self.products.save_data()
			self.config.set_state(menu_items[idx])
			self._load_products_to_the_list()

	def _remove_dep_name(self, full_name):
		# full name means product: department
		pos = full_name.find(u':')
		if pos > 0:
			name = full_name[:pos]
		else:
			name = full_name
		return name

	def _load_products_to_the_list(self):
		self.products = Products(self.config.get_list_file())

		self.products_list = Listbox(self.products.get_checked(), self.products_list_handler)

		# bind the handler to key 5
		self.products_list.ui_list.bind(0x35, self.products_list_handler)
		self._bind_cursor_movements(self.products_list)
		self._bind_move_up_down(self.products_list)

		appuifw.app.body = self.products_list.ui_list
		appuifw.app.title = self.__compose_the_title()

	def _bind_cursor_movements(self, lst):
		# bind the handler to key 2
		lst.ui_list.bind(0x32, self.products_list.cb_focus_up)
		# bind the handler to key 8
		lst.ui_list.bind(0x38, self.products_list.cb_focus_down)

	def _bind_move_up_down(self, lst):
		# bind the handler to key 7
		lst.ui_list.bind(0x37, self.products_list.cb_move_up)
		# bind the handler to key 9
		lst.ui_list.bind(0x39, self.products_list.cb_move_down)

	def __compose_the_title(self):
		return u"%s %s" % (ShoppingList.TITLE, self.config.get_state().title())

	def products_list_handler(self):
		name = self.products_list.current_item()
		if self.product_mode:
			# remove department name
			if name != EMPTY_LIST_MARK:
				self.products.put_out_list(self._remove_dep_name(name))
				self.products_list.remove_item(name)
		else:
			self.products.sync_departments_order(self.products_list.lst)
			lst = self.products.get_checked_by_dep(name)
			self.products_list.set_list(lst if len(lst) else [EMPTY_LIST_MARK, ])
			appuifw.app.menu[1] = (ShoppingList.BY_DEPARTMENTS, self.at_mode)
			appuifw.app.title = self.__compose_the_title() + u'. ' + name
			self.product_mode = True

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

		# switch mode to product
		self.product_mode = False
		self.at_mode()

	def at_add_product(self):
		appuifw.app.title = u'Add a new item. Select a department.'
		departs = self.products.get_departs_list()
		idx = appuifw.selection_list(departs, search_field=1)
		if not idx == None:
			depart_name = departs[idx]
			appuifw.app.title = u'Add a new item.'
			prod_name = appuifw.query(u'Enter an item name.', 'text')
			# : used to separate product name and department in 'by depart' mode
			if prod_name and u':' not in prod_name:
				if not prod_name.lower() in self.products.get_all_products():
					# return 1 - cannot add, otherwise - 0
					if self.products.add_product(prod_name.lower(), depart_name):
						appuifw.note(u"Cannot add the item.\n%s" % self.products.last_msg, "error")
					else:
						self.products_list.add_item(prod_name.lower())
				else:
					appuifw.note(u'%s has been at the list.' % prod_name.lower(), "error")
			else:
				pass  # 'cancel' was pressed on product name
		else:
			pass  # 'cancel' was pressed on department name
		appuifw.app.title = ShoppingList.TITLE

	def at_remove_product(self):
		appuifw.app.title = u'Remove goods. Select a department.'
		lst = self.products.get_all_products()
		idx = appuifw.selection_list(lst, search_field=1)
		if not idx == None:
			prod_name = lst[idx]
			if appuifw.query(u"Remove %s?" % prod_name, "query") == 1:
				self.products.remove_product(prod_name)
				self.products_list.remove_item(prod_name)
		appuifw.app.title = ShoppingList.TITLE

	def at_add_depart(self):
		appuifw.app.title = u'Add a new department.'
		depart_name = appuifw.query(u'Add a depart name.', 'text')
		if depart_name and self.products.add_depart(depart_name):
				appuifw.note(u'%s' % self.products.last_msg, 'error')
		appuifw.app.title = ShoppingList.TITLE
		appuifw.note(u'%s added.' % depart_name, 'info')

	def at_remove_depart(self):
		appuifw.app.title = u'Remove a department.'
		lst = self.products.get_departs_list()
		idx = appuifw.selection_list(lst, search_field=1)
		if not idx == None:
			depart_name = lst[idx]
			if appuifw.query(u"Remove %s?" % depart_name, "query") == 1 \
				and self.products.remove_depart(depart_name):
					appuifw.note(u"%s" % self.products.last_msg, "error")
		appuifw.app.title = ShoppingList.TITLE

	def at_back(self):
		assert hasattr(self, '_previous_app'), 'No previous app attributes'
		appuifw.app.title = self._previous_app['title']
		appuifw.app.body = self._previous_app['body']
		appuifw.app.menu = self._previous_app['menu']

	def at_help(self):
		help_f = os.path.join(ListConfig.get_path_to_resources(), 'help.txt')
		if os.path.isfile(help_f):
			f = open(help_f, 'r')
			text = unicode(f.read())
			f.close()
			t = appuifw.Text()
			t.font = u"LatinPlain8"  # sets font to Latin Plain 8
			t.color = (0, 0, 0)  # blue
			t.set(text)
			t.set_pos(0)
			self._previous_app = {
				'title': appuifw.app.title,
				'body': appuifw.app.body,
				'menu': appuifw.app.menu,
			}
			appuifw.app.title = u'Help'
			appuifw.app.body = t
			appuifw.app.menu = [ (u'Back', self.at_back) ]
		else:
			appuifw.note(u'No help found in the resources', "error")

	def about(self):
		appuifw.note(u'The list v.%s' % __version__, "info")

	def quit(self):
		self.products.save_data()
		appuifw.app.exit_key_handler = None
		self.script_lock.signal()


if __name__ == '__main__':
	ShoppingList()
