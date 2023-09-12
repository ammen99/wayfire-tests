import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hello World")

        self.button = Gtk.Button(label="Click Here")
        self.button.set_tooltip_markup("This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. This is a Tooltip. ")
        self.add(self.button)

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
win.maximize()
Gtk.main()
