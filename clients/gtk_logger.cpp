// A simple program which opens a window and logs pointer events on it.
#include <gtkmm.h>
#include "log.hpp"

#include <gdk/gdkwayland.h>
#include <wayland-client.h>

#include <pointer-constraints-unstable-v1-client-protocol.h>

enum class log_features : int
{
    POINTER     = (1 << 0),
    KEYBOARD    = (1 << 1),
    TOUCH       = (1 << 2),
    CONSTRAINTS = (1 << 3),
    CLICK_TO_X  = (1 << 4),
};

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

// ----------------------------- wl_keyboard impl ------------------------------
static void handle_keymap(void*, wl_keyboard*, uint32_t, int32_t, uint32_t)
{
    // no-op
}

static void handle_keyboard_enter(void*, wl_keyboard*, uint32_t, wl_surface*, wl_array*)
{
    logger::log("keyboard-enter");
}

void handle_keyboard_leave(void*, wl_keyboard*, uint32_t, wl_surface*)
{
    logger::log("keyboard-leave");
}

static void handle_keyboard_key(void*, wl_keyboard*, uint32_t, uint32_t,
    uint32_t key, uint32_t state)
{
    if (state == WL_KEYBOARD_KEY_STATE_PRESSED)
    {
        logger::log("key-press " + std::to_string(key));
    } else
    {
        logger::log("key-release " + std::to_string(key));
    }
}

static void handle_keyboard_modifiers(void*, wl_keyboard*, uint32_t, uint32_t,
    uint32_t, uint32_t, uint32_t)
{
    // no-op
}

static void handle_keyboard_repeat_info(void*, wl_keyboard*, int32_t, int32_t)
{
    // no-op
}

const struct wl_keyboard_listener keyboard_logger = {
    .keymap = handle_keymap,
    .enter = handle_keyboard_enter,
    .leave = handle_keyboard_leave,
    .key = handle_keyboard_key,
    .modifiers = handle_keyboard_modifiers,
    .repeat_info = handle_keyboard_repeat_info,
};
// ------------------------------ wl_touch impl --------------------------------
static void handle_touch_down(void*, wl_touch*, uint32_t, uint32_t, wl_surface *,
    int32_t id, wl_fixed_t x, wl_fixed_t y)
{
    int xx = std::round(wl_fixed_to_double(x));
    int yy = std::round(wl_fixed_to_double(y));
    logger::log("touch-down " + std::to_string(id) + " " + std::to_string(xx)
        + " " + std::to_string(yy));
}

static void handle_touch_up(void*, wl_touch*, uint32_t, uint32_t, int32_t id)
{
    logger::log("touch-up " + std::to_string(id));
}

static void handle_touch_motion(void*, wl_touch*, uint32_t,
    int32_t id, wl_fixed_t x, wl_fixed_t y)
{
    int xx = std::round(wl_fixed_to_double(x));
    int yy = std::round(wl_fixed_to_double(y));
    logger::log("touch-motion " + std::to_string(id) + " " + std::to_string(xx)
        + " " + std::to_string(yy));
}

static void handle_touch_frame(void*,
    wl_touch*)
{
    // no-op
}

static void handle_touch_cancel(void*, wl_touch*)
{
    logger::log("touch-cancel");
}

static void handle_touch_shape(void*, wl_touch*, int32_t, wl_fixed_t, wl_fixed_t)
{
    // no-op
}

static void handle_touch_orientation(void*, wl_touch*, int32_t, wl_fixed_t)
{
    // no-op
}

const struct wl_touch_listener touch_logger = {
	.down        = handle_touch_down,
	.up          = handle_touch_up,
	.motion      = handle_touch_motion,
	.frame       = handle_touch_frame,
	.cancel      = handle_touch_cancel,
	.shape       = handle_touch_shape,
	.orientation = handle_touch_orientation,
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

struct wl_keyboard_listener listener;

static struct
{
    wl_pointer *pointer = NULL;
    wl_keyboard *keyboard = NULL;
    wl_touch *touch = NULL;
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

static void setup_window(Gtk::Window *win, int flags)
{
    auto btn = new Gtk::Button("Test");
    win->add(*btn);

    // Ensures all wayland stuff is set up
    win->show_all();

    auto disp = Gdk::Display::get_default();
    auto gdk_pointer = disp->get_default_seat()->get_pointer();
    auto wl_seat = gdk_wayland_device_get_wl_seat(gdk_pointer->gobj());

    if (flags & (int)log_features::POINTER)
    {
        global_protocols.pointer = wl_seat_get_pointer(wl_seat);
        wl_pointer_add_listener(global_protocols.pointer, &pointer_logger, NULL);
    }

    if (flags & (int)log_features::KEYBOARD)
    {
        global_protocols.keyboard = wl_seat_get_keyboard(wl_seat);
        wl_keyboard_add_listener(global_protocols.keyboard, &keyboard_logger, NULL);
    }

    if (flags & (int)log_features::TOUCH)
    {
        global_protocols.touch = wl_seat_get_touch(wl_seat);
        wl_touch_add_listener(global_protocols.touch, &touch_logger, NULL);
    }

    if (flags & (int)log_features::CONSTRAINTS)
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

    if (flags & (int)log_features::CLICK_TO_X)
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

    int flags = 0;
    for (int i = 3; i < argc; i++)
    {
        if (!strcmp("confine", argv[i]))
        {
            flags |= (int)log_features::CONSTRAINTS;
        }
        if (!strcmp("pointer", argv[i]))
        {
            flags |= (int)log_features::POINTER;
        }
        if (!strcmp("touch", argv[i]))
        {
            flags |= (int)log_features::TOUCH;
        }
        if (!strcmp("keyboard", argv[i]))
        {
            flags |= (int)log_features::KEYBOARD;
        }
        if (!strcmp("click-to-close", argv[i]))
        {
            flags |= (int)log_features::CLICK_TO_X;
        }
    }

    setup_window(&a, flags);
    app->run(a);
    return 0;
}
