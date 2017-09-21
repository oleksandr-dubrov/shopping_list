#import
import xml.etree.ElementTree as ET
import os, e32, appuifw

#TODO:
#1 Don't ask the question to quit.
#2 Fix info menu
#3 When the list is empty and the user adds a new product, then the new product appears in the list with the empty list mark.

#TODO for next version:
#1 Sort the products in all lists by alphabet or by departments
#2 add ukrainian language


EMPTY_LIST_MARK = unicode('The shopping list is empty.')
XML_DATA_FILE = 'e:\\data\\python\\products.xml'

class Listbox():
	'''Extends appyifw Listbox'''
	
	def __init__(self, init_list, cb_handler):
		self.lst = init_list if len(init_list) else [EMPTY_LIST_MARK,]
		self._ui_list = appuifw.Listbox(self.lst, cb_handler)
	
	def currectItem(self):
		idx = self._ui_list.current()
		return self.lst[idx]
	
	def add_item(self, item):
		self.lst.append(item)
		self._ui_list.set_list(self.lst, self._ui_list.current())
	
	def remove_item(self, item):
		self.lst.remove(item)
		if len(self.lst) == 0: #cannot set an empty list
			self.lst = [EMPTY_LIST_MARK,]
		self._ui_list.set_list(self.lst, self._ui_list.current())
		
	def set_list(self, lst):
		self.lst = lst
		self._ui_list.set_list(lst, self._ui_list.current())
		
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
		self._departs, self._products = self._getData(xml_file)
		self.last_msg = u''
		
	def _getData(self, xml_file):
		# Get a list of products.
		# Each product is a dict with a name and a flag (is in list)
		self.tree = ET.parse(xml_file)
		self.root = self.tree.getroot()
		assert self.root.tag == 'products', 'unknown xml'
		products = [] #it is going to be a list of dictionaries
		departs = []
		for depart in self.root:
			departs.append(depart.attrib)
			for prod in depart:
				products.append(prod.attrib)
		return departs, products
	
	def saveData(self):
		for depart in self.root:
			for prod in depart:
				for p in self._products:
					if prod.attrib['name'] == p['name']:
						prod.attrib['inlist'] = p['inlist']
						break
		self.tree.write(self._xml_file)
		
	@property
	def products(self):
		return self._products
	
	@property
	def departments(self):
		return self._departs
	
	def putInList(self, name):
		self._setInlistVal(name, '1')
				
	def putOutList(self, name):
		self._setInlistVal(name, '0')
		
	def _setInlistVal(self, name, value):
		def cb_setter(item):
			if item['name'] == name:
				item['inlist'] = value
			return item
		self._products = map(cb_setter, self._products)
	
	def getAllProducts(self):
		return [unicode(x['name']) for x in self._products]
		
	def getChecked(self):
		#return a list of names that are checked
		return [unicode(x['name']) for x in self._products if x['inlist'] == '1']
	
	def getUnchecked(self):
		#return a list of names that are NOT checked
		return [unicode(x['name']) for x in self._products if x['inlist'] == '0']
	
	def getDepartsList(self):
		return [unicode(x['name']) for x in self._departs]
	
	def getCheckedByDep(self, name):
		if not name:
			return self.getChecked()
		
		for depart in self.root:
			if depart.attrib['name'] == name:
				return [prod.attrib['name'] + ': ' + name for prod in depart if prod.attrib['inlist'] == '1']
		return []
	
	def addProduct(self, name, depart_name):
		#check if the product has already been in the list
		if unicode(name) in [unicode(x['name']) for x in self._products]:
			self.last_msg = u'The product has already been in the list.'
			return 1
		#update the product list
		product = {'name': name, 'inlist': '1'}
		self._products.append(product)
		#update the xml tree
		for depart in self.root:
			if depart.attrib['name'] == depart_name:
				ET.SubElement(depart, 'product', product)
				return 0
		self.last_msg = u'%s is not found'%depart_name
		return 1
	
	def removeProduct(self, name):
		for x in self._products:
			if x['name'] == name:
				#udate the tree
				for depart in self.root:
					for prod in depart:
						if prod.attrib['name'] == name:
							depart.remove(prod)
							#update the list
							self._products.remove(x)
							return 0
		self.last_msg = u'The product is not in the list.'
		return 1
	
	def addDepart(self, name):
		for depart in self.root:
			if depart.attrib['name'] == name:
				self.last_msg = u'A department with name %s has been in the list'%name
				return 1
		new_dep = {'name': name}
		ET.SubElement(self.root, 'department', new_dep)
		self._departs.append(new_dep)
		return 0
	
	def removeDepart(self, name):
		for x in self._departs:
			if x['name'] == name:
				for depart in self.root:
					if depart.attrib['name'] == name:
						self.root.remove(depart)
						#udate the list
						self._departs.remove(x)
						return 0		
		self.last_msg = u'The department is not in the list'
		return 1
	
class ShoppingList:
	''' The Application class.'''
	
	TITLE = u"Shopping list"
	
	def __init__(self):
		appuifw.app.title = ShoppingList.TITLE
		appuifw.app.screen = "normal"
		
		self.products = Products(XML_DATA_FILE)
		
		self.products_list = Listbox(self.products.getChecked(), self.products_list_handler)
		appuifw.app.body = self.products_list.ui_list
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
							(u'Info', self.about),
							]
		self.product_mode = True

		#next two lines lock the main thread, so they should be at the end of __init__ when everything has been created.
		self.script_lock = e32.Ao_lock()
		self.script_lock.wait()
		
	def at_list_manager(self):
		menu_items =	 [u'Add product',	  u'Remove product',	  u'Add departament', u'Remove departament']
		menu_item_foo = [self.at_addProduct, self.at_removeProduct, self.at_addDepart,  self.at_removeDepart]
		idx = appuifw.popup_menu(menu_items)
		if not idx == None:
			menu_item_foo[idx]()
			
	def at_mode(self):
		if self.product_mode:
			appuifw.app.title = u"Shopping list. Departments." 
			appuifw.app.menu[1] = (u'All products', self.at_mode)
			self.products_list.set_list([u'-- All departments',] + self.products.getDepartsList())
			self.product_mode = False
		else:
			appuifw.app.title = ShoppingList.TITLE
			appuifw.app.menu[1] = (u'By departments', self.at_mode)
			self.products_list.set_list(self.products.getChecked())
			self.product_mode = True
		
	def _removeDepName(self, full_name):
		#full name means product: department
		pos = full_name.find(u':')
		if pos > 0:
			name = full_name[:pos]
		else:
			name = full_name
		return name

	def products_list_handler(self):
		name = self.products_list.currectItem()
		if self.product_mode:
			#remove department name
			if name != EMPTY_LIST_MARK:
				self.products.putOutList(self._removeDepName(name))
				self.products_list.remove_item(name)
		else:
			lst = self.products.getCheckedByDep(name if not name.startswith(u'--') else None)
			self.products_list.set_list(lst if len(lst) else [EMPTY_LIST_MARK,])
			self.product_mode = True
		
	def run(self):
		pass
	
	def at_home(self):
		appuifw.app.title = u"At home. Select a product to buy."
		unchecked = self.products.getUnchecked()
		if len(unchecked) == 0:
			appuifw.note(u"Everything has been added to the shopping list.", "info")
		else:
			idxs = appuifw.multi_selection_list(unchecked, style='checkbox', search_field=1)
			for idx in idxs:
				self.products.putInList(unchecked[idx])
			self.products_list.set_list(self.products.getChecked())

		#switch mode to product
		self.product_mode = False
		self.at_mode()
	
	def at_addProduct(self):
		appuifw.app.title = u'Add a new product. Select a department.'
		departs = self.products.getDepartsList()
		idx = appuifw.selection_list(departs, search_field=1)
		if not idx == None:
			depart_name = departs[idx]
			appuifw.app.title = u'Add a new product.'
			prod_name = appuifw.query(u'Enter a product name.', 'text')
			if prod_name and not u':' in prod_name: # : used to separate product name and department in 'by depart' mode
				if not prod_name.lower() in self.products.getAllProducts():
					if self.products.addProduct(prod_name.lower(), depart_name):#return 1 - cannot add, otherwise - 0
						appuifw.note(u"Cannot add the product.\n%s"%self.products.last_msg, "error")
					else:
						self.products_list.add_item(prod_name.lower())
				else:
					appuifw.note(u'%d has been at the list.'%prod_name.lower())
			else:
				pass # 'cancel' was presssed on product name
		else:
			pass # 'cancel' was pressed on department name
		appuifw.app.title = ShoppingList.TITLE
		
	def at_removeProduct(self):
		appuifw.app.title = u'Remove a new product. Select a department.'
		lst = self.products.getAllProducts()
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
				appuifw.note(u'%s'%self.last_msg, 'error')
		appuifw.app.title = ShoppingList.TITLE
	
	def at_removeDepart(self):
		appuifw.app.title = u'Remove a department.'
		lst = self.products.getDepartsList()
		idx = appuifw.selection_list(lst, search_field=1)
		if not idx == None:
			depart_name = lst[idx]
			if appuifw.query(u"Remove %s?"%depart_name, "query") == 1:
				if self.products.removeDepart(depart_name):
					appuifw.note(u"%s"%self.products.last_msg, "error")
		appuifw.app.title = ShoppingList.TITLE
					
	def about(self):
		appuifw.note(u'Shopping list v.1.0\n * - add a product\n C - remove a current product\n	2 - up\n 8 - down\n	5 - check a current product0',
					"info")

	def quit(self):
		#if appuifw.query(u"Quit?", "query") == 1:
		self.products.saveData()
		appuifw.app.exit_key_handler = None
		self.script_lock.signal()


if __name__ == '__main__':
	ShoppingList().run()
