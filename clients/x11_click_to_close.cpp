// Simple program which closes itself on right click.
// Supports either starting with a particular geometry or fullscreen:
//
// ./x11_click_to_close <class> X Y W H
// ./x11_click_to_close <class> fullscreen
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>

int main(int argc, char **argv) {
    bool set_fullscreen = 0;
    int x = 0;
    int y = 0;
    int width = 100;
    int height = 100;

    if (argc <= 3) {
        set_fullscreen = 1;
    } else {
        x = atoi(argv[2]);
        y = atoi(argv[3]);
        width = atoi(argv[4]);
        height = atoi(argv[5]);
    }

    auto display = XOpenDisplay(NULL);
    auto screen = DefaultScreen(display);

    // Create window
    auto window = XCreateSimpleWindow(display, RootWindow(display, screen),
        x, y, width, height, 0, BlackPixel(display, screen), WhitePixel(display, screen));

    // Set app-id so that tests can know which window is which
    XSelectInput(display, window, ButtonPressMask);
    XClassHint hint;
    hint.res_class = hint.res_name = argv[1];
    XSetClassHint(display, window, &hint);
    XStoreName(display, window, argv[1]);

    // Map the window
    XMapWindow(display, window);


    // Set fullscreen if needed
    if (set_fullscreen) {
        Atom fullscreen   = XInternAtom(display, "_NET_WM_STATE_FULLSCREEN", False);
        Atom net_wm_state = XInternAtom(display, "_NET_WM_STATE", False);

        XEvent fsevent;
        memset(&fsevent, 0, sizeof(fsevent));
        fsevent.type = ClientMessage;

        fsevent.xclient.message_type = net_wm_state;
        fsevent.xclient.display = display;
        fsevent.xclient.window = window;
        fsevent.xclient.format = 32;
        fsevent.xclient.data.l[0] = 1;
        fsevent.xclient.data.l[1] = (long)fullscreen;
        XSendEvent(display, XDefaultRootWindow(display), False, SubstructureRedirectMask, &fsevent);
    } else {
        // Manually configure so that wayfire gets the correct position
        XWindowChanges xws;
        xws.x = x;
        xws.y = y;
        XConfigureWindow(display, window, CWX | CWY, &xws);
    }

    XEvent event;
    bool running = true;
    while (running) {
        XNextEvent(display, &event);
        switch (event.type) {
          case ButtonPress:
            if (event.xbutton.button == Button3) {
                running = false;
            }

            break;
        }
    }

    XDestroyWindow(display, window);
    XCloseDisplay(display);
    return 0;
}
