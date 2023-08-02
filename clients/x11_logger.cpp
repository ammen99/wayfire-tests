#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <unistd.h>
#include <cstdint>

#include "log.hpp"

int main(int argc, char **argv) {
    auto display = XOpenDisplay(NULL);
    auto screen = DefaultScreen(display);

    // Create window
    auto window = XCreateSimpleWindow(display, RootWindow(display, screen), 0, 0, 250, 250, 0,
        BlackPixel(display, screen), WhitePixel(display, screen));
    XSelectInput(display, window, (1 << 25) - 1);

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
          case FocusIn:
            if (event.xfocus.detail == NotifyPointer || event.xfocus.detail == NotifyPointerRoot) break;
            logger::log("focus-in");
            break;
          case FocusOut:
            if (event.xfocus.detail == NotifyPointer || event.xfocus.detail == NotifyPointerRoot) break;
            logger::log("focus-out");
            break;
          default:
            break;
        }
    }

    return 0;
}
