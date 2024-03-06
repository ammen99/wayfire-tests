// A simple program which opens a window and logs pointer events on it.
#include <gtkmm.h>
#include "gtkmm/enums.h"
#include "gtkmm/menubutton.h"
#include "gtkmm/popover.h"
#include "log.hpp"

#include <gdk/gdkwayland.h>
#include <string>
#include <wayland-client.h>

#include <pointer-constraints-unstable-v1-client-protocol.h>
#include <tablet-unstable-v2-client-protocol.h>

enum class log_features : int
{
    POINTER     = (1 << 0),
    KEYBOARD    = (1 << 1),
    TOUCH       = (1 << 2),
    CONSTRAINTS = (1 << 3),
    CLICK_TO_X  = (1 << 4),
    CLICK_TO_MENU    = (1 << 5),
    TABLET           = (1 << 6),
    DIALOG_SHORTCUT  = (1 << 7),
    DELAY_DIALOG     = (1 << 8),
    TEXT_INPUT       = (1 << 9),
};

// ---------------------------- wl_pointer impl --------------------------------
wl_surface *dialog_wl_surface = NULL;
wl_surface *current_surface = NULL;
bool emit_enter_coords = false; // for compat with older tests

void handle_pointer_enter(void*, struct wl_pointer*, uint32_t,
    struct wl_surface* surface, wl_fixed_t surface_x, wl_fixed_t surface_y)
{
    int x = std::round(wl_fixed_to_double(surface_x));
    int y = std::round(wl_fixed_to_double(surface_y));
    std::string suffix = emit_enter_coords ? (" " + std::to_string(x) + "," + std::to_string(y)) : "";

    current_surface = surface;
    if (surface == dialog_wl_surface) {
        logger::log("pointer-enter-dialog" + suffix);
    } else {
        logger::log("pointer-enter" + suffix);
    }
}

void handle_pointer_leave(void*, struct wl_pointer*, uint32_t,
    struct wl_surface* surface)
{
    if (surface == dialog_wl_surface) {
        logger::log("pointer-leave-dialog");
    } else {
        logger::log("pointer-leave");
    }

    current_surface = NULL;
}

void handle_pointer_motion(void*, struct wl_pointer*, uint32_t,
    wl_fixed_t surface_x, wl_fixed_t surface_y)
{
    int x = std::round(wl_fixed_to_double(surface_x));
    int y = std::round(wl_fixed_to_double(surface_y));

    std::string prefix = (current_surface == dialog_wl_surface) ? "dialog-" : "";
    logger::log(prefix + "pointer-motion " + std::to_string(x) + "," + std::to_string(y));
}

void handle_pointer_button(void*, struct wl_pointer*,
    uint32_t, uint32_t, uint32_t button, uint32_t state)
{
    std::string prefix = (current_surface == dialog_wl_surface) ? "dialog-" : "";
    if (state == WL_POINTER_BUTTON_STATE_PRESSED)
    {
        logger::log(prefix + "button-press " + std::to_string(button));
    } else
    {
        logger::log(prefix + "button-release " + std::to_string(button));
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

void handle_pointer_axis120(void*, struct wl_pointer*, uint32_t, int32_t)
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
    .axis_value120 = handle_pointer_axis120,
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

#undef wl_array_for_each
#define wl_array_for_each(pos, array) for (pos = (uint32_t*)(array)->data; \
        (const char *) pos < ((const char *) (array)->data + (array)->size); (pos)++)

static void handle_keyboard_enter(void*, wl_keyboard*, uint32_t, wl_surface*, wl_array* array)
{
    logger::log("keyboard-enter");
    uint32_t *item;
    wl_array_for_each(item, array)
    {
        logger::log("key-enter " + std::to_string(*item));
    }
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

// ----------------------------- tablet-v2 impl --------------------------------

void handle_tablet_tool_type(void*, zwp_tablet_tool_v2 *, uint32_t)
{
    // nothing
}

void handle_tablet_tool_hardware_serial(void*, zwp_tablet_tool_v2*, uint32_t, uint32_t)
{
    // nothing
}

void handle_tablet_tool_hardware_id_wacom(void*, zwp_tablet_tool_v2*, uint32_t, uint32_t)
{
    // nothing
}

void handle_tablet_tool_capability(void*, zwp_tablet_tool_v2*, uint32_t)
{
    // nothing
}

void handle_tablet_tool_done(void*, zwp_tablet_tool_v2*)
{
    // nothing
}

void handle_tablet_tool_removed(void*, zwp_tablet_tool_v2*)
{
    // nothing
}

void handle_tablet_tool_proximity_in(void*, zwp_tablet_tool_v2*, uint32_t, zwp_tablet_v2*, wl_surface*)
{
    logger::log("tool-proximity-in");
}

void handle_tablet_tool_proximity_out(void*, zwp_tablet_tool_v2*)
{
    logger::log("tool-proximity-out");
}

void handle_tablet_tool_down(void*, zwp_tablet_tool_v2*, uint32_t)
{
    logger::log("tool-down");
}

void handle_tablet_tool_up(void*, zwp_tablet_tool_v2*)
{
    logger::log("tool-up");
}

void handle_tablet_tool_motion(void*, zwp_tablet_tool_v2*, wl_fixed_t surface_x, wl_fixed_t surface_y)
{
    int x = std::round(wl_fixed_to_double(surface_x));
    int y = std::round(wl_fixed_to_double(surface_y));
    logger::log("tool-motion " + std::to_string(x) + "," + std::to_string(y));
}

void handle_tablet_tool_pressure(void*, zwp_tablet_tool_v2*, uint32_t pressure)
{
    logger::log("tool-pressure " + std::to_string(pressure));
}

void handle_tablet_tool_distance(void*, zwp_tablet_tool_v2*, uint32_t)
{
    //nothing
}

void handle_tablet_tool_tilt(void*, zwp_tablet_tool_v2*, wl_fixed_t, wl_fixed_t)
{
    //nothing
}

void handle_tablet_tool_rotation(void*, zwp_tablet_tool_v2*, wl_fixed_t)
{
    //nothing
}

void handle_tablet_tool_slider(void*, zwp_tablet_tool_v2*, int32_t)
{
    //nothing
}

void handle_tablet_tool_wheel(void*, zwp_tablet_tool_v2*, wl_fixed_t, int32_t)
{
    //nothing
}

void handle_tablet_tool_button(void*, zwp_tablet_tool_v2*, uint32_t, uint32_t button, uint32_t state)
{
    if (state != ZWP_TABLET_TOOL_V2_BUTTON_STATE_RELEASED)
    {
        logger::log("tool-button-press " + std::to_string(button));
    } else
    {
        logger::log("tool-button-release " + std::to_string(button));
    }
}

void handle_tablet_tool_frame(void*, zwp_tablet_tool_v2*, uint32_t)
{
    // nothing
}

const zwp_tablet_tool_v2_listener tool_listener = {
	.type = handle_tablet_tool_type,
	.hardware_serial = handle_tablet_tool_hardware_serial,
	.hardware_id_wacom = handle_tablet_tool_hardware_id_wacom,
	.capability = handle_tablet_tool_capability,
	.done = handle_tablet_tool_done,
	.removed = handle_tablet_tool_removed,
	.proximity_in = handle_tablet_tool_proximity_in,
	.proximity_out = handle_tablet_tool_proximity_out,
	.down = handle_tablet_tool_down,
	.up = handle_tablet_tool_up,
	.motion = handle_tablet_tool_motion,
	.pressure = handle_tablet_tool_pressure,
	.distance = handle_tablet_tool_distance,
	.tilt = handle_tablet_tool_tilt,
	.rotation = handle_tablet_tool_rotation,
	.slider = handle_tablet_tool_slider,
	.wheel = handle_tablet_tool_wheel,
	.button = handle_tablet_tool_button,
	.frame = handle_tablet_tool_frame,
};

void handle_tablet_pad_group(void*, zwp_tablet_pad_v2*, zwp_tablet_pad_group_v2*)
{
    // nothing to do
}

void handle_tablet_pad_path(void*, zwp_tablet_pad_v2*, const char*)
{
    // nothing to do
}

void handle_tablet_pad_buttons(void*, zwp_tablet_pad_v2*, uint32_t)
{
    // nothing to do
}

void handle_tablet_pad_done(void*, zwp_tablet_pad_v2*)
{
    // nothing to do
}

void handle_tablet_pad_button(void*, zwp_tablet_pad_v2*, uint32_t, uint32_t button, uint32_t state)
{
    if (state == ZWP_TABLET_PAD_V2_BUTTON_STATE_PRESSED)
    {
        logger::log("pad-button-press " + std::to_string(button));
    } else
    {
        logger::log("pad-button-release " + std::to_string(button));
    }
}

void handle_tablet_pad_enter(void*, zwp_tablet_pad_v2*, uint32_t, zwp_tablet_v2*, wl_surface*)
{
    logger::log("pad-enter");
}

void handle_tablet_pad_leave(void*, zwp_tablet_pad_v2*, uint32_t, wl_surface*)
{
    logger::log("pad-leave");
}

void handle_tablet_pad_removed(void*, zwp_tablet_pad_v2*)
{
    // nothing to do
}

static const zwp_tablet_pad_v2_listener pad_listener = {
	.group = handle_tablet_pad_group,
	.path = handle_tablet_pad_path,
	.buttons = handle_tablet_pad_buttons,
	.done = handle_tablet_pad_done,
	.button = handle_tablet_pad_button,
	.enter = handle_tablet_pad_enter,
	.leave = handle_tablet_pad_leave,
	.removed = handle_tablet_pad_removed,
};

void handle_tablet_added(void*, zwp_tablet_seat_v2*, zwp_tablet_v2*)
{
    // nothing to do
}

void handle_tablet_tool_added(void*, zwp_tablet_seat_v2*, zwp_tablet_tool_v2* tool)
{
    zwp_tablet_tool_v2_add_listener(tool, &tool_listener, NULL);
}

void handle_tablet_pad_added(void*, zwp_tablet_seat_v2*, zwp_tablet_pad_v2* pad)
{
    zwp_tablet_pad_v2_add_listener(pad, &pad_listener, NULL);
}

static const zwp_tablet_seat_v2_listener tablet_seat_listener = {
    .tablet_added = handle_tablet_added,
    .tool_added = handle_tablet_tool_added,
    .pad_added = handle_tablet_pad_added,
};

// ---------------------------- wl_registry impl -------------------------------
zwp_pointer_constraints_v1 *pointer_constraints = NULL;
zwp_tablet_manager_v2 *tablet_manager = NULL;

static void registry_add_object(void*, struct wl_registry *registry,
    uint32_t name, const char *interface, uint32_t version)
{
    if (strcmp(interface, zwp_pointer_constraints_v1_interface.name) == 0)
    {
        pointer_constraints = (zwp_pointer_constraints_v1*)
            wl_registry_bind(registry, name, &zwp_pointer_constraints_v1_interface, std::min(version, 1u));
    }

    if (strcmp(interface, zwp_tablet_manager_v2_interface.name) == 0)
    {
        tablet_manager = (zwp_tablet_manager_v2*)
            wl_registry_bind(registry, name, &zwp_tablet_manager_v2_interface, 1u);
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
    zwp_tablet_seat_v2 *tablet = NULL;

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
    if (flags & (int)log_features::TEXT_INPUT)
    {
        Gtk::Entry *entry = new Gtk::Entry();
        entry->set_text("");
        win->add(*entry);
    } else if (flags & (int)log_features::CLICK_TO_MENU)
    {
        Gtk::MenuButton *mb = new Gtk::MenuButton();
        mb->set_label("Menu");

        Gtk::Popover *popover = new Gtk::Popover();
        Gtk::Label *label = new Gtk::Label("Label");
        label->show_all();
        popover->add(*label);
        popover->set_size_request(200, 200);
        popover->set_position(Gtk::PositionType::POS_BOTTOM);
        mb->set_popover(*popover);
        win->add(*mb);
    } else
    {
        auto btn = new Gtk::Button("Test");
        win->add(*btn);

        if (flags & (int)log_features::CLICK_TO_X)
        {
            btn->signal_button_press_event().connect_notify([=] (GdkEventButton*)
            {
                win->close();
            });
        }
    }

    // Ensures all wayland stuff is set up
    win->show_all();

    auto disp = Gdk::Display::get_default();
    auto gdk_pointer = disp->get_default_seat()->get_pointer();
    auto wl_seat = gdk_wayland_device_get_wl_seat(gdk_pointer->gobj());

    wl_display *wl_disp = gdk_wayland_display_get_wl_display(disp->gobj());
    wl_registry *registry = wl_display_get_registry(wl_disp);
    wl_registry_add_listener(registry, &registry_listener, NULL);
    wl_display_roundtrip(wl_disp);

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

    if (flags & (int)log_features::TABLET)
    {
        global_protocols.tablet = zwp_tablet_manager_v2_get_tablet_seat(tablet_manager, wl_seat);
        zwp_tablet_seat_v2_add_listener(global_protocols.tablet, &tablet_seat_listener, NULL);
    }

    if (flags & (int)log_features::CONSTRAINTS)
    {
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

    if (flags & (int)log_features::DIALOG_SHORTCUT)
    {
        win->signal_key_press_event().connect_notify([flags, win] (GdkEventKey *button)
        {
            if (button->keyval == GDK_KEY_o)
            {
                Glib::signal_timeout().connect_once([=] () {
                    auto dialog = new Gtk::Dialog();
                    dialog->set_title("TestDialog");
                    dialog->set_default_size(100, 100);
                    const bool delay_dialog = (flags & (int)log_features::DELAY_DIALOG);
                    if (!delay_dialog)
                    {
                        dialog->set_transient_for(*win);
                    }

                    dialog->show_all();
                    dialog_wl_surface = gdk_wayland_window_get_wl_surface(dialog->get_window()->gobj());
                    if (delay_dialog)
                    {
                        Glib::signal_timeout().connect_once([dialog, win] () {
                            dialog->set_transient_for(*win);
                        }, 100);
                    }
                }, 50);
            }
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
        if (!strcmp("click-to-menu", argv[i]))
        {
            flags |= (int)log_features::CLICK_TO_MENU;
        }
        if (!strcmp("tablet", argv[i]))
        {
            flags |= (int)log_features::TABLET;
        }
        if (!strcmp("dialog-shortcut", argv[i]))
        {
            flags |= (int)log_features::DIALOG_SHORTCUT;
        }
        if (!strcmp("emit-enter-coords", argv[i]))
        {
            emit_enter_coords = true;
        }
        if (!strcmp("delay-dialog", argv[i]))
        {
            flags |= (int)log_features::DELAY_DIALOG;
        }
        if (!strcmp("text-input", argv[i]))
        {
            flags |= (int)log_features::TEXT_INPUT;
        }
    }

    if ((flags & (int)log_features::CLICK_TO_MENU) &&
        (flags & (int)log_features::CLICK_TO_X))
    {
        std::cout << "Can't do click to x and click to menu at the same time!" << std::endl;
        return EXIT_FAILURE;
    }

    setup_window(&a, flags);
    app->run(a);
    return 0;
}
