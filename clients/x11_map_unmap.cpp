// Simple program which closes itself on right click.
// Supports either starting with a particular geometry or fullscreen:
//
// ./x11_click_to_close <class> X Y W H
// ./x11_click_to_close <class> fullscreen
#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <unistd.h>
#include <getopt.h>

int main(int argc, char **argv) {
    double delay;
    int x, y, width, height, reps;
    char *app_id;
    bool override_redirect = false;

    int opt;
    while ((opt = getopt(argc, argv, "a:x:y:w:h:d:r:o")) != -1) {
        switch (opt) {
          case 'a':
            app_id = strdup(optarg);
            break;
          case 'o':
            override_redirect = true;
            break;
          case 'x':
            x = atoi(optarg);
            break;
          case 'y':
            y = atoi(optarg);
            break;
          case 'w':
            width = atoi(optarg);
            break;
          case 'h':
            height = atoi(optarg);
            break;
          case 'd':
            delay = atof(optarg);
            break;
          case 'r':
            reps = atoi(optarg);
            break;
          default:
            break;
        }
    }

    auto display = XOpenDisplay(NULL);
    auto screen = DefaultScreen(display);

    XSetWindowAttributes attrs;
    attrs.background_pixel = WhitePixel(display, screen);
    attrs.event_mask = ExposureMask;
    attrs.override_redirect = override_redirect;

    // Create window
    auto window = XCreateWindow(display, RootWindow(display, screen), x, y, width, height, 0,
        CopyFromParent, InputOutput, CopyFromParent, CWEventMask | CWBackPixel | CWOverrideRedirect, &attrs);

    // Set app-id so that tests can know which window is which
    XClassHint hint;
    hint.res_class = hint.res_name = app_id;
    XSetClassHint(display, window, &hint);
    XStoreName(display, window, app_id);

    // Map the window
    XMapWindow(display, window);

    // Manually configure so that wayfire gets the correct position
    XWindowChanges xws;
    xws.x = x;
    xws.y = y;
    XConfigureWindow(display, window, CWX | CWY, &xws);

    XEvent event;
    const auto& wait_for_map = [&] ()
    {
        while (true) {
            XNextEvent(display, &event);
            if (event.type == Expose)
                break;
        }
    };

    wait_for_map();

    for (int i = 0; i < reps; i++) {
        if (delay > 0) {
            usleep(delay*1000);
        }

        XUnmapWindow(display, window);
        XFlush(display);
        if (delay > 0) {
            usleep(delay*1000);
        }

        XMapWindow(display, window);
        XFlush(display);
        wait_for_map();
    }

    while (true) {
        XNextEvent(display, &event);
    }

    return 0;
}
