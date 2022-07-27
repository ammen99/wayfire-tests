// A simple program which opens a window and waits for drag-and-drop action.
// Once a drop operation completes, the window who received the operation closes itself.
#include <gtkmm.h>

int cnt_created = 0;

static void setup_window(Gtk::Window *win)
{
    std::vector<Gtk::TargetEntry> types;
    types.push_back(Gtk::TargetEntry("private-gtk-dnd"));

    win->drag_source_set(types);
    win->drag_dest_set(types);

    win->signal_drag_drop().connect_notify([win] (auto, auto, auto, auto)
    {
        win->close();
    });
}

int main(int argc, char **argv)
{
    auto app = Gtk::Application::create();

    Gtk::Window a;
    a.set_default_size(200, 200);
    a.set_title(argv[1] ?: "null");
    setup_window(&a);

    a.show_all();
    app->run(a);
    return 0;
}
