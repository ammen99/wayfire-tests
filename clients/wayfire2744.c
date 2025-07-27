/*
 * wlr-crasher.c -- simple program to demonstrate a crash in wlroots
 * 	(based on wlroots examples)
 * 
 * 2020-2024 Daniel Kondor <kondor.dani@gmail.com>
 */

#define WLR_USE_UNSTABLE
#define _GNU_SOURCE         /* See feature_test_macros(7) */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <sys/mman.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <wayland-client.h>
#include <wayland-server.h>
#include "xdg-shell-client-protocol.h"

struct wl_compositor *compositor = NULL;
struct xdg_wm_base *wm_base = NULL;

static void handle_global(void *data, struct wl_registry *registry,
		uint32_t name, const char *interface, uint32_t version) {
    (void)data;
    (void)version;

	if(strcmp(interface, wl_compositor_interface.name) == 0) {
		compositor = wl_registry_bind(registry, name,
			&wl_compositor_interface, 1);
	} else if(strcmp(interface, xdg_wm_base_interface.name) == 0) {
		wm_base = wl_registry_bind(registry, name, &xdg_wm_base_interface, 1);
	}
}

static void handle_global_remove(void *data, struct wl_registry *registry, uint32_t name) {
    (void)data;
    (void)registry;
    (void)name;
}

static const struct wl_registry_listener registry_listener = {
	.global = handle_global,
	.global_remove = handle_global_remove,
};

int main()
{
	struct wl_display *display = wl_display_connect(NULL);
	struct wl_registry *registry = wl_display_get_registry(display);
	wl_registry_add_listener(registry, &registry_listener, NULL);
	wl_display_roundtrip(display);

    struct wl_surface *surface = wl_compositor_create_surface(compositor);
	assert(surface);
	struct xdg_surface *xdg_surface = xdg_wm_base_get_xdg_surface(wm_base, surface);
	assert(xdg_surface);
	struct xdg_toplevel *xdg_toplevel = xdg_surface_get_toplevel(xdg_surface);
	assert(xdg_toplevel);
    xdg_toplevel_set_maximized(xdg_toplevel);
	wl_display_roundtrip(display);
    xdg_toplevel_unset_maximized(xdg_toplevel);
	wl_display_roundtrip(display);
	wl_surface_commit(surface);
	wl_display_roundtrip(display);
	return 0;
}

