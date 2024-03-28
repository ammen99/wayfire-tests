import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class TestWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Test Window")
        self.connect("destroy", self.on_destroy)
        self.set_size_request(200, 200)
        self.label = Gtk.Label(label="Test Window")
        self.add(self.label)
        self.show_all()

    def on_destroy(self, window):
        Gtk.main_quit()


def open_close_window():
    window = TestWindow()
    GLib.timeout_add(50, close_window, window)


def close_window(window):
    window.destroy()
    return False


def main():
    while True:
        open_close_window()
        Gtk.main()


if __name__ == "__main__":
    main()
