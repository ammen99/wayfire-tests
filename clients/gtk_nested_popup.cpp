#include <gtkmm.h>

int main()
{
    auto app = Gtk::Application::create();
    Gtk::Window win;

    Gtk::Menu menu;
    Gtk::MenuItem item1{"Item"};
    menu.append(item1);

    Gtk::Menu nested;
    Gtk::MenuItem nested1{"Nested"};
    nested.append(nested1);
    item1.set_submenu(nested);

    nested.signal_show().connect([&] () {
        nested.property_rect_anchor_dx() = -50;
    });

    win.signal_button_press_event().connect_notify([&] (GdkEventButton *event)
    {
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
