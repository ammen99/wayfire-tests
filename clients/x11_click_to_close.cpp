// Simple program which closes itself on right click.
// Supports either starting with a particular geometry or fullscreen:
//
// ./x11_click_to_close <class> X Y W H
// ./x11_click_to_close <class> fullscreen
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <stdlib.h>
#include <iostream>

int main(int argc, char **argv) {
    bool set_fullscreen = 0;
    int x = 0;
    int y = 0;
    int width = 1;
    int height = 1;

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

    // Set fullscreen if needed
    if (set_fullscreen) {
        Atom atoms[2] = {
            XInternAtom(display, "_NET_WM_STATE_FULLSCREEN", False),
            None
        };

        XChangeProperty(display, window, XInternAtom(display, "_NET_WM_STATE", False),
            XA_ATOM, 32, PropModeReplace, (unsigned char*)atoms, 1);
    }

    // Set app-id so that tests can know which window is which
    XSelectInput(display, window, ButtonPressMask | ButtonReleaseMask | PointerMotionMask);
    XClassHint hint;
    hint.res_class = hint.res_name = argv[1];
    XSetClassHint(display, window, &hint);

    // Map the window
    XMapRaised(display, window);

    if (!set_fullscreen) {
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
        std::cout << "Any event" << std::endl;

        switch (event.type) {
          case ButtonPress:
            std::cout << "Got " << event.xbutton.button << " "
                << event.xbutton.x << " " << event.xbutton.y << " "<< event.xbutton.state << std::endl;

            if (event.xbutton.button == Button3) {
                running = false;
            }

            break;
          case ButtonRelease:
            std::cout << "Released " << event.xbutton.button << std::endl;
            break;
          case PointerMotionMask:
            std::cout << "Moved " << event.xmotion.x << " "<< event.xmotion.y << std::endl;
            break;
        }
    }

    XDestroyWindow(display, window);
    XCloseDisplay(display);
    return 0;
}
