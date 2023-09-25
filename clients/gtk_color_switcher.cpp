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
#include <glib-unix.h>

#include <glibmm.h>

int cur_color = 0;

std::string colors[] = {
    "red",
    "green",
    "blue",
};

int handle_usr1(gpointer user_data)
{
    auto win = (Gtk::Window*)user_data;
    win->override_background_color(Gdk::RGBA(colors[cur_color]));
    cur_color = (cur_color + 1) % 3;
    return G_SOURCE_CONTINUE;
}

int main(int argc, char **argv)
{
    auto app = Gtk::Application::create();

    Gtk::Window a;
    a.set_default_size(200, 200);
    a.set_title(argv[1] ?: "null");

    a.show_all();
    g_unix_signal_add_full(G_PRIORITY_DEFAULT, SIGUSR1, handle_usr1, &a, NULL);

    if (argc >= 3)
    {
        // We have logging enabled
        logger::init(argc, argv);
        a.signal_draw().connect_notify([=] (auto)
        {
            logger::log("signal-draw");
        });
    }

    app->run(a);
    return 0;
}
