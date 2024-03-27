#include <gtkmm.h>
#include <gtk-layer-shell.h>

int main()
{
    auto app = Gtk::Application::create();
    Gtk::Window win;
    gtk_layer_init_for_window(win.gobj());
    gtk_layer_set_keyboard_interactivity(win.gobj(), 0);
    gtk_layer_set_layer(win.gobj(), GTK_LAYER_SHELL_LAYER_TOP);

    Gtk::Menu menu;
    Gtk::MenuItem item1{"Item"};
    Gtk::MenuItem item2{"Close"};
    menu.append(item1);
    menu.append(item2);
    menu.set_size_request(200, 100);
    item2.signal_activate().connect([] () { std::exit(0); });

    win.signal_button_press_event().connect_notify([&] (GdkEventButton *event) {
        if (event->button == 3)
        {
            menu.attach_to_widget(win);
            menu.popup_at_pointer((GdkEvent*)event);
            menu.show_all();
        }
    });

    win.set_size_request(200, 200);
    win.show_all();
    app->run(win);
}
