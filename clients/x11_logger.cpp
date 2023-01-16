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

#include "log.hpp"

int main(int argc, char **argv) {
    auto display = XOpenDisplay(NULL);
    auto screen = DefaultScreen(display);

    XSetWindowAttributes attrs;
    attrs.background_pixel = WhitePixel(display, screen);
    attrs.event_mask = ExposureMask | KeyPressMask | KeyReleaseMask | KeymapStateMask;
    attrs.override_redirect = 1;

    // Create window
    auto window = XCreateWindow(display, RootWindow(display, screen), 0, 0, 100, 100, 0,
        CopyFromParent, InputOutput, CopyFromParent, CWEventMask | CWBackPixel | CWOverrideRedirect, &attrs);

    // Set app-id so that tests can know which window is which
    XClassHint hint;
    hint.res_class = hint.res_name = argv[1];
    XSetClassHint(display, window, &hint);
    XStoreName(display, window, argv[1]);

    // Map the window
    XMapWindow(display, window);

    logger::init(argc, argv);

    XEvent event;
    while (true) {
        XNextEvent(display, &event);
        switch (event.type) {
          case Expose:
            break;
          case KeyPress:
            logger::log("key-press " + std::to_string(event.xkey.keycode));
            break;
          case KeyRelease:
            logger::log("key-release " + std::to_string(event.xkey.keycode));
            break;
          default:;
            //logger::log("nothing " + std::to_string(event.type));
        }
    }

    return 0;
}
