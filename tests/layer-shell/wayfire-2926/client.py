#!/usr/bin/env python3

import os
import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')

from gi.repository import Gtk, GtkLayerShell

class SimpleWindow(Gtk.Window):
	def __init__(self):
		self.timeout_id = 0
		Gtk.Window.__init__(self)
		GtkLayerShell.init_for_window(self)
		GtkLayerShell.set_respect_close(self, True) # does not matter
		GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
		GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
		GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
		GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, 3000) # put a large enough number
		GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 3000) # to get an impossible arrangement

		lbl = Gtk.Label.new('label')
		self.add(lbl)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()


def main():
	SimpleWindow()
	Gtk.main()
	return 0

if __name__ == '__main__':
	sys.exit(main())
