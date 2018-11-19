#!/usr/bin/env python
# -*- coding: utf-8 -*-


# this is a module for debugging


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


class Text:
    def __init__(self):
        font = None  # @UnusedVariable
        color = None  # @UnusedVariable
        highlight_color = None  # @UnusedVariable

    def set(self, msg):
        print(msg)

    def set_pos(self, pos):
        pass


class Canvas:
    def __init__(self, event_callback=None, redraw_callback=None, resize_callback=None):
        self.size = (240, 234)

    def rectangle(self, coords, fill):
        printd("Rectangle with coodrs (%d, %d, %d, %d) and filled with (%d, %d, %d)" %
               (coords + fill))

    def line(self, coords, width, outline):
        printd("Line with coords (%d, %d, %d, %d) outlined by (%d, %d, %d)" %
               (coords + outline))

    def measure_text(self, text, font):
        dummy_coords = ((0, -18, 54, 3),)  # spokij
        printd(u"Measure text %s" % (text))
        printd("Return (%d, %d, %d, %d)" % (dummy_coords[0]))
        return dummy_coords

    def text(self, coords, text, fill, font):
        utext = u''.join(text if text else '')
        printd(u"Print text %s with coords (%d, %d)" % ((utext,) + coords))
        if not utext == ' ':
            print ('    %s' % utext)
            print (' +---------------------+-------------------+')


class Listbox:
    def __init__(self, lst, handler):
        pass


def note(text, tp):
    print ("Note %s: %s" % (text, tp))


def query(msg, tp):
    if tp == "query":
        print (msg)
        o = raw_input('0 - no, 1 - yes.\n')
        if o == '0':
            return 0
        else:
            return 1
    elif tp == "text":
        o = raw_input('%s\n' % msg)
        return unicode(o, 'utf-8')


def selection_list(lst, search_field=0):
    print ('+ Choose an item.')
    for idx in range(len(lst)):
        print ('%d - %s' % (idx, lst[idx]))

    print ('%d - Go to the main menu' % (len(lst)))
    o = raw_input(' -> ')
    try:
        if int(o) == len(lst):
            return None
        else:
            return int(o)
    except ValueError as e:
        print ('Wrong input: %s' % e)
        return selection_list(lst, search_field=search_field)


def multi_selection_list(lst, style='checkbox', search_field=0):
    assert lst and len(lst), 'no list or the list is empty'
    assert len(lst) < 12, 'the list is to long'
    print ('Choose an item')
    for idx in range(len(lst)):
        print ('%d. %s' % (idx, lst[idx]))
    o = raw_input()
    ret = []
    try:
        for idx in range(len(o)):
            ret.append(int(o[idx]))
    except ValueError as e:
        print ('Wrong input: %s' % e)
        multi_selection_list(lst, style='checkbox', search_field=search_field)
    return ret


EKeyLeftSoftkey = 0x01
EKeyYes = 0x02
EKeyMenu = 0x03
EKey0 = 0x04
EKey1 = 0x05
EKey2 = 0x06
EKey3 = 0x07
EKey4 = 0x08
EKey5 = 0x09
EKey6 = 0x10
EKey7 = 0x11
EKey8 = 0x12
EKey9 = 0x13
EKeyStar = 0x14
EKeyLeftArrow = 0x15
EKeyUpArrow = 0x16
EKeySelect = 0x17
EKeyRightArrow = 0x18
EKeyDownArrow = 0x19
EKeyRightSoftkey = 0x20
EKeyNo = 0x21
EKeyBackspace = 0x22
EKeyEdit = 0x23
EKeyHash = 0x24

EScancode1 = 0x30
EScancode1 = 0x31
EScancode2 = 0x32
EScancode3 = 0x33
EScancode4 = 0x34
EScancode5 = 0x35
EScancode6 = 0x36
EScancode7 = 0x37
EScancode8 = 0x38
EScancode9 = 0x39

EEventKey = 0x51
