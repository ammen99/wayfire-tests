// A simple program which opens a GTK window and changes its color depending on values from stdin
#include <cstdio>
#include <gtkmm.h>
#include <unistd.h>
#include "gdkmm/pixbuf.h"
#include "gdkmm/rgba.h"
#include "glibmm/iochannel.h"
#include "glibmm/main.h"
#include "glibmm/refptr.h"
#include "log.hpp"

int main(int, char **argv)
{
    auto app = Gtk::Application::create();

    Gtk::Window a;
    a.set_default_size(200, 200);
    a.set_title(argv[1] ?: "null");

    a.show_all();
    Glib::signal_io().connect([&a] (Glib::IOCondition) -> bool {
        std::string s;
        std::cin >> s;
        a.override_background_color(Gdk::RGBA(s));
        return true;
    }, STDIN_FILENO, Glib::IO_IN);
    app->run(a);
    return 0;
}
