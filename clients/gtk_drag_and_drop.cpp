// A simple program which opens a window and waits for drag-and-drop action.
// The drag-and-drop action is logged to a file.
#include <gtkmm.h>
#include "gdkmm/pixbuf.h"
#include "glibmm/refptr.h"
#include "log.hpp"

int cnt_created = 0;

Glib::RefPtr<Gdk::Pixbuf> load_dnd_icon(int size)
{
    auto icon_theme = Gtk::IconTheme::get_default();
    return icon_theme->load_icon("address-book-new", size)->scale_simple(size, size, Gdk::INTERP_BILINEAR);
}

static void setup_window(Gtk::Window *win)
{
    std::vector<Gtk::TargetEntry> types;
    types.push_back(Gtk::TargetEntry("private-gtk-dnd"));

    win->drag_source_set(types);
    win->drag_dest_set(types);
    win->drag_source_set_icon(load_dnd_icon(400));

    win->signal_drag_begin().connect_notify([] (auto)
    {
        logger::log("drag-begin");
    });

    win->signal_drag_end().connect_notify([] (auto)
    {
        logger::log("drag-end");
    });

    win->signal_drag_drop().connect_notify([] (auto, auto, auto, auto)
    {
        logger::log("drag-drop");
    });
}

int main(int argc, char **argv)
{
    logger::init(argc, argv);
    auto app = Gtk::Application::create();

    Gtk::Window a;
    a.set_default_size(200, 200);
    a.set_title(argv[1] ?: "null");
    setup_window(&a);

    a.show_all();
    app->run(a);
    return 0;
}
