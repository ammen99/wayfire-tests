// A simple program which opens a window and waits for drag-and-drop action.
// The drag-and-drop action is logged to a file.
#include <gtkmm.h>
#include "log.hpp"

int cnt_created = 0;

static void setup_window(Gtk::Window *win)
{
    auto btn = new Gtk::Button("test");
    win->add(*btn);

    btn->signal_button_press_event().connect_notify([] (GdkEventButton *ev)
    {
        logger::log("button-press " + std::to_string(ev->button));
    });

    btn->signal_button_release_event().connect_notify([] (GdkEventButton *ev)
    {
        logger::log("button-release " + std::to_string(ev->button));
    });

    btn->signal_enter_notify_event().connect_notify([] (GdkEventCrossing *ev)
    {
        logger::log("pointer-enter");
    });

    btn->signal_leave_notify_event().connect_notify([] (GdkEventCrossing *ev)
    {
        logger::log("pointer-leave");
    });

    btn->signal_motion_notify_event().connect_notify([] (GdkEventMotion *ev)
    {
        logger::log("pointer-motion " + std::to_string((int)std::round(ev->x)) +
            "," + std::to_string((int)std::round(ev->y)));
    });

    btn->set_events(btn->get_events() | Gdk::ALL_EVENTS_MASK);
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
