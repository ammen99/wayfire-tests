// A simple program which opens a window and logs pointer events on it.
#include <gtkmm.h>
#include "log.hpp"

#include <gdk/gdkwayland.h>
#include <wayland-client.h>

#include <pointer-constraints-unstable-v1-client-protocol.h>


// ---------------------------- wl_pointer impl --------------------------------
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

// ------------------------ zwp_confined_pointer_v1 impl -----------------------
static void handle_pointer_confined(void*, zwp_confined_pointer_v1*)
{
    logger::log("pointer-confined");
}

static void handle_pointer_unconfined(void*, zwp_confined_pointer_v1*)
{
    logger::log("pointer-unconfined");
}

static const struct zwp_confined_pointer_v1_listener confined_pointer_impl = {
    .confined = handle_pointer_confined,
    .unconfined = handle_pointer_unconfined,
};

// ---------------------------- wl_registry impl -------------------------------
zwp_pointer_constraints_v1 *pointer_constraints = NULL;

static void registry_add_object(void*, struct wl_registry *registry,
    uint32_t name, const char *interface, uint32_t version)
{
    if (strcmp(interface, zwp_pointer_constraints_v1_interface.name) == 0)
    {
        pointer_constraints = (zwp_pointer_constraints_v1*) wl_registry_bind(
            registry, name, &zwp_pointer_constraints_v1_interface,
            std::min(version, 1u));
    }
}

static void registry_remove_object(void *, struct wl_registry*,
    uint32_t) { /* no-op */ }

static struct wl_registry_listener registry_listener =
{
    &registry_add_object,
    &registry_remove_object
};

static struct
{
    wl_pointer *pointer = NULL;
    zwp_confined_pointer_v1 *confined = NULL;

} global_protocols;

static wl_region *get_region_for_window(Gtk::Window *win)
{
    auto disp = Gdk::Display::get_default();
    wl_compositor *compositor = gdk_wayland_display_get_wl_compositor(disp->gobj());
    wl_region *region = wl_compositor_create_region(compositor);
    wl_region_add(region, 0, 0,
        win->get_allocated_width(), win->get_allocated_height());

    return region;
}

void setup_constraint(Gtk::Window *win)
{
    auto region = get_region_for_window(win);
    zwp_confined_pointer_v1_set_region(global_protocols.confined, region);
    wl_region_destroy(region);
    wl_surface_commit(gdk_wayland_window_get_wl_surface(win->get_window()->gobj()));
}

static void setup_window(Gtk::Window *win, bool do_confine, bool click_to_close)
{
    auto btn = new Gtk::Button("Test");
    win->add(*btn);

    // Ensures all wayland stuff is set up
    win->show_all();

    auto disp = Gdk::Display::get_default();
    auto gdk_pointer = disp->get_default_seat()->get_pointer();
    auto wl_seat = gdk_wayland_device_get_wl_seat(gdk_pointer->gobj());
    global_protocols.pointer = wl_seat_get_pointer(wl_seat);
    wl_pointer_add_listener(global_protocols.pointer, &pointer_logger, NULL);

    if (do_confine)
    {
        wl_display *wl_disp = gdk_wayland_display_get_wl_display(disp->gobj());
        wl_registry *registry = wl_display_get_registry(wl_disp);
        wl_registry_add_listener(registry, &registry_listener, NULL);
        wl_display_roundtrip(wl_disp);

        auto region = get_region_for_window(win);
        auto wl_surf = gdk_wayland_window_get_wl_surface(win->get_window()->gobj());
        global_protocols.confined = zwp_pointer_constraints_v1_confine_pointer(pointer_constraints,
            wl_surf, global_protocols.pointer, region, ZWP_POINTER_CONSTRAINTS_V1_LIFETIME_PERSISTENT);
        wl_region_destroy(region);
        zwp_confined_pointer_v1_add_listener(global_protocols.confined, &confined_pointer_impl, NULL);

        win->signal_size_allocate().connect_notify([=] (auto&)
        {
            setup_constraint(win);
        });
    }

    if (click_to_close)
    {
        btn->signal_button_press_event().connect_notify([=] (GdkEventButton*)
        {
            win->close();
        });
    }
}

int main(int argc, char **argv)
{
    logger::init(argc, argv);
    auto app = Gtk::Application::create();

    Gtk::Window a;
    a.set_default_size(200, 200);
    a.set_title(argv[1] ?: "null");

    bool do_confine = (argc >= 4 && std::string(argv[3]) == "confine");
    bool click_to_close = (argc >= 5 && std::string(argv[4]) == "click-to-close");

    setup_window(&a, do_confine, click_to_close);
    app->run(a);
    return 0;
}
