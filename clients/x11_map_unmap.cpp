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

int main(int, char **argv) {
    int x = atoi(argv[3]);
    int y = atoi(argv[4]);
    int width = atoi(argv[5]);
    int height = atoi(argv[6]);

    auto display = XOpenDisplay(NULL);
    auto screen = DefaultScreen(display);

    XSetWindowAttributes attrs;
    attrs.background_pixel = WhitePixel(display, screen);
    attrs.event_mask = ExposureMask;
    attrs.override_redirect = 1;

    // Create window
    auto window = XCreateWindow(display, RootWindow(display, screen), x, y, width, height, 0,
        CopyFromParent, InputOutput, CopyFromParent, CWEventMask | CWBackPixel | CWOverrideRedirect, &attrs);

    // Set app-id so that tests can know which window is which
    XClassHint hint;
    hint.res_class = hint.res_name = argv[1];
    XSetClassHint(display, window, &hint);
    XStoreName(display, window, argv[1]);

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
    XUnmapWindow(display, window);
    XFlush(display);

    XMapWindow(display, window);
    XFlush(display);
    wait_for_map();

    XUnmapWindow(display, window);
    XFlush(display);

    // Create a second black window

    // Create window
    attrs.background_pixel = BlackPixel(display, screen);
    auto window2 = XCreateWindow(display, RootWindow(display, screen), x, y, width, height, 0,
        CopyFromParent, InputOutput, CopyFromParent, CWEventMask | CWBackPixel | CWOverrideRedirect, &attrs);

    // Set app-id so that tests can know which window is which
    hint.res_class = hint.res_name = argv[2];
    XSetClassHint(display, window2, &hint);
    XStoreName(display, window2, argv[2]);

    // Map the window
    XMapWindow(display, window2);
    while (true) {
        XNextEvent(display, &event);
    }

    return 0;
}
