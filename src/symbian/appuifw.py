#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is a module for debugging
# it mocks the real modules from PyS60

__version__ = '1.0'

DBG_MODE = False
def printd(self, *args):
	if DBG_MODE:
		msg = '| log :'
		msg += ' '.join(str(args))
		print msg

class app:
		body = None
		title = None
		screen = None
		exit_key_handler = None
		menu = None

class Canvas:
	def __init__(self, event_callback=None, redraw_callback=None, resize_callback=None):
		self.size = (240, 234)
	
	def rectangle(self, coords, fill):
		printd("Rectangle with coodrs (%d, %d, %d, %d) and filled with (%d, %d, %d)"%(coords + fill))
		
	def line(self, coords, width, outline):
		printd("Line with coords (%d, %d, %d, %d) outlined by (%d, %d, %d)"%(coords + outline))
		
	def measure_text(self, text, font):
		dummy_coords = ((0, -18, 54, 3),) #spokij
		printd(u"Measure text %s"%(text))
		printd("Return (%d, %d, %d, %d)"%(dummy_coords[0]))
		return dummy_coords
	
	def text(self, coords, text, fill, font):
		utext = u''.join(text)
		printd(u"Print text %s with coords (%d, %d)"%((utext,) + coords))
		if not utext == ' ':
			print ' +-------------------------------------+'
			print '	%s'%utext
			print ' +-------------------------------------+'

		
class Listbox:
	def __init__(self, lst, handler):
		self.lst = lst
	
	def bind(self, event, cb):
		''' bind keys event to the callback '''
		pass
	
	def set_list(self, lst, cur):
		self.lst = lst
	
	def current(self):
		assert self.lst, 'my assumption that the list shouldn\'t be empty'
		return 0
	
	
def note(text, tp):
	print "Note %s: %s"%(text, tp)

def query(msg, tp):
	if tp == "query":
		o = raw_input('0 - no, 1 - yes.\n')
		if o == '0':
			return 0
		else:
			return 1
	elif tp == "text":
		o = raw_input('%s\n'%msg)
		return unicode(o, 'utf-8')
	else:
		pass
	
def selection_list(lst, search_field=0):
	print '+ Choose an item.'
	for idx in range(len(lst)):
		print '%d - %s'%(idx, lst[idx])
	o = raw_input(' -> ')
	try:
		return int(o)
	except ValueError as e:
		print 'Wrong input: %s'%e
		return selection_list(lst, search_field=search_field)


def multi_selection_list(lst, style='checkbox', search_field=0):
	assert lst and len(lst), 'no list or the list is empty'
	assert len(lst) < 12, 'the list is to long'
	print 'Choose an item'
	for idx in range(len(lst)):
		print '%d. %s'%(idx, lst[idx])
	o = raw_input('->')
	ret = []
	try:
		for idx in range(len(o)):
			ret.append(int(o[idx]))
	except ValueError as e:
		print 'Wrong input: %s'%e
		multi_selection_list(lst, style='checkbox', search_field=search_field)
	return ret

def popup_menu(menu_items):
	'''show popup menu from the menu_items
	return the selected item's number'''
	for idx in range(len(menu_items)):
		print '%d. %s'%(idx, menu_items[idx])
	o = raw_input('This is a popup menu. Chose something:')
	if o not in range(len(menu_items)-1):
		print 'Wrong input %s. Try again.', o
		popup_menu(menu_items)
	else:
		return o
		
	


EKeyLeftSoftkey				= 0x01
EKeyYes						= 0x02
EKeyMenu					= 0x03
EKey0						= 0x04
EKey1						= 0x05
EKey2						= 0x06
EKey3						= 0x07
EKey4						= 0x08
EKey5						= 0x09
EKey6						= 0x10
EKey7						= 0x11
EKey8						= 0x12
EKey9						= 0x13
EKeyStar					= 0x14
EKeyLeftArrow				= 0x15
EKeyUpArrow					= 0x16
EKeySelect					= 0x17
EKeyRightArrow				= 0x18
EKeyDownArrow				= 0x19
EKeyRightSoftkey			= 0x20
EKeyNo						= 0x21
EKeyBackspace				= 0x22
EKeyEdit					= 0x23
EKeyHash					= 0x24

EScancodeLeftSoftkey		= 0x26
EScancodeYes				= 0x27
EScancodeMenu				= 0x28
EScancode0					= 0x29
EScancode1					= 0x30
EScancode2					= 0x31
EScancode3					= 0x32
EScancode4					= 0x33
EScancode5					= 0x34
EScancode6					= 0x35
EScancode7					= 0x36
EScancode8					= 0x37
EScancode9					= 0x38
EScancodeStar				= 0x39
EScancodeLeftArrow			= 0x40
EScancodeUpArrow			= 0x41
EScancodeSelect				= 0x42
EScancodeRightArrow			= 0x43
EScancodeDownArrow			= 0x44
EScancodeRightSoftkey		= 0x45
EScancodeNo					= 0x46
EScancodeBackspace			= 0x47
EScancodeEdit				= 0x48
EScancodeHash				= 0x49

EEventKeyDown				= 0x50
EEventKey					= 0x51
EEventKeyUp					= 0x52
