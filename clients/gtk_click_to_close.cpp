// A simple program which opens a window and dialogs
// with nested structure as described in the command line argument.
// A dialog closes itself if clicked on.

// ./gtk_click_to_close a -> Just main window with title a
// ./gtk_click_to_close a b -> Main window with title a with dialog b
// ./gtk_click_to_close a b c -> Main window with title a with dialogs b, c
// ./gtk_click_to_close a b c d -> Main window with title a with dialogs b, c, c has nested dialog d
#include <gtkmm.h>

static void setup_window(Gtk::Window *win)
{
    win->signal_button_press_event().connect_notify([win] (GdkEventButton *button)
    {
        if (button->button == GDK_BUTTON_SECONDARY)
        {
            win->close();
        }
    });
}

int main(int argc, char **argv)
{
    Gtk::Window *a = NULL, *b = NULL, *c = NULL, *d = NULL;

    auto app = Gtk::Application::create();

    a = new Gtk::Window;
    a->set_default_size(200, 200);
    setup_window(a);

    a->set_title(argv[1]);
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

    if (argc >= 5) {
        d = new Gtk::MessageDialog(*c, "Test");
        d->set_title(argv[4]);
        setup_window(d);
    }

    for (auto x : {a, b, c, d})
    {
        if (x)
        {
            x->show_all();
        }
    }

    app->run(*a);
    return 0;
}
