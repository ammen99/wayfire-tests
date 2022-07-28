all:
	g++ x11_click_to_close.cpp -o x11_click_to_close -lX11
	g++ gtk_special.cpp -o gtk_special `pkg-config --cflags --libs gtkmm-3.0`
	g++ gtk_drag_and_drop.cpp -o gtk_drag_and_drop `pkg-config --cflags --libs gtkmm-3.0`
	g++ gtk_logger.cpp -o gtk_logger `pkg-config --cflags --libs gtkmm-3.0`
