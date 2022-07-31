// A simple program which opens a window and logs pointer events on it.
#include <gtkmm.h>
#include "log.hpp"

#include <gdk/gdkwayland.h>
#include <wayland-client.h>

void handle_pointer_enter(void*, struct wl_pointer*, uint32_t,
    struct wl_surface*, wl_fixed_t, wl_fixed_t)
{
    logger::log("pointer-enter");
}

void handle_pointer_leave(void*, struct wl_pointer*, uint32_t,
    struct wl_surface*)
{
    logger::log("pointer-leave");
}

void handle_pointer_motion(void*, struct wl_pointer*, uint32_t,
    wl_fixed_t surface_x, wl_fixed_t surface_y)
{
    int x = std::round(wl_fixed_to_double(surface_x));
    int y = std::round(wl_fixed_to_double(surface_y));
    logger::log("pointer-motion " + std::to_string(x) + "," + std::to_string(y));
}

void handle_pointer_button(void*, struct wl_pointer*,
    uint32_t, uint32_t, uint32_t button, uint32_t state)
{
    if (state == WL_POINTER_BUTTON_STATE_PRESSED)
    {
        logger::log("button-press " + std::to_string(button));
    } else
    {
        logger::log("button-release " + std::to_string(button));
    }
}

void handle_pointer_axis(void*, struct wl_pointer*,
    uint32_t, uint32_t, wl_fixed_t)
{
    // no-op
}

void handle_pointer_frame(void*, struct wl_pointer*)
{
    // no-op
}

void handle_pointer_axis_source(void*, struct wl_pointer*,
    uint32_t)
{
    // no-op
}

void handle_pointer_axis_stop(void*, struct wl_pointer*,
    uint32_t, uint32_t)
{
    // no-op
}

void handle_pointer_axis_discrete(void*, struct wl_pointer*,
    uint32_t, int32_t)
{
    // no-op
}

const struct wl_pointer_listener pointer_logger = {
    .enter = handle_pointer_enter,
    .leave = handle_pointer_leave,
    .motion = handle_pointer_motion,
    .button = handle_pointer_button,
    .axis = handle_pointer_axis,
    .frame = handle_pointer_frame,
    .axis_source = handle_pointer_axis_source,
    .axis_stop = handle_pointer_axis_stop,
    .axis_discrete = handle_pointer_axis_discrete,
};

static void setup_window(Gtk::Window *win)
{
    auto btn = new Gtk::Button("Test");
    win->add(*btn);

    // Ensures all wayland stuff is set up
    win->show_all();

    auto disp = Gdk::Display::get_default();
    auto gdk_pointer = disp->get_default_seat()->get_pointer();
    auto wl_seat = gdk_wayland_device_get_wl_seat(gdk_pointer->gobj());
    auto pointer = wl_seat_get_pointer(wl_seat);
    wl_pointer_add_listener(pointer, &pointer_logger, NULL);
}

int main(int argc, char **argv)
{
    logger::init(argc, argv);
    auto app = Gtk::Application::create();

    Gtk::Window a;
    a.set_default_size(200, 200);
    a.set_title(argv[1] ?: "null");
    setup_window(&a);
    app->run(a);
    return 0;
}
