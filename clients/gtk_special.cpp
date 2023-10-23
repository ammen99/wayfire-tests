// A simple program which opens a window and dialogs
// with nested structure as described in the command line argument.
//
// All of the created windows close themselves if they receive a right click.
// In addition, keyboard interaction is supported too:
// q -> close window and subwindows

// ./gtk_special a -> Just main window with title a
// ./gtk_special a b -> Main window with title a with dialog b
// ./gtk_special a b c -> Main window with title a with dialogs b, c
// ./gtk_special a b c d -> Main window with title a with dialogs b, c, c has nested dialog d
#include "glibmm/main.h"
#include <gtkmm.h>

int cnt_created = 0;

static void setup_window(Gtk::Window *win)
{
    win->signal_button_press_event().connect_notify([win] (GdkEventButton *button)
    {
        if (button->button == GDK_BUTTON_SECONDARY)
        {
            win->close();
        }
    });

    win->signal_key_press_event().connect_notify([win] (GdkEventKey *button)
    {
        Gtk::Window *w;
        switch (button->keyval)
        {
          case GDK_KEY_o:
            w = new Gtk::MessageDialog(*win, "test");
            w->set_title("auto" + std::to_string(cnt_created));
            ++cnt_created;
            setup_window(w);
            w->show_all();

          default:
            // do nothing
            ;
        }
    });

    win->signal_key_release_event().connect_notify([win] (GdkEventKey *button)
    {
        switch (button->keyval)
        {
          case GDK_KEY_q:
            win->close();
            break;
          default:
            // do nothing
            ;
        }
    });

    win->show_all();
}

int main(int argc, char **argv)
{
    Gtk::Window *a = NULL, *b = NULL, *c = NULL, *d = NULL;

    auto app = Gtk::Application::create();

    a = new Gtk::Window;
    a->set_default_size(200, 200);
    a->set_title(argv[1]);
    setup_window(a);

    // Create dialogs after a timeout.
    // Without a timeout, GTK3 has a bug: it sets the parent too early, so that it is unmapped, which according
    // to the xdg spec is a no-op
    Glib::signal_timeout().connect_once([&] ()
    {
        if (argc >= 3) {
            b = new Gtk::MessageDialog(*a, "Test");
            b->set_title(argv[2]);
            setup_window(b);
        }

        if (argc >= 4) {
            c = new Gtk::MessageDialog(*a, "Test");
            c->set_title(argv[3]);
            setup_window(c);
        }

        Glib::signal_timeout().connect_once([&] () {
            if (argc >= 5) {
                d = new Gtk::MessageDialog(*c, "Test");
                d->set_title(argv[4]);
                setup_window(d);
            }
        }, 50);
    }, 50);

    app->run(*a);
    return 0;
}
