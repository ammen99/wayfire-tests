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
    auto provider = Gtk::CssProvider::create();
    provider->load_from_data(".myclass { background-color: red; } .myclass2 { background-color: green; }");
    Gtk::StyleContext::add_provider_for_screen(Gdk::Screen::get_default(), provider, GTK_STYLE_PROVIDER_PRIORITY_USER);
    item1.get_style_context()->add_class("myclass");
    nested1.get_style_context()->add_class("myclass2");

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
