#include <gtk/gtk.h>
#include <gtk-layer-shell/gtk-layer-shell.h>

gboolean timeout(void* window) {
    gtk_layer_set_exclusive_zone(GTK_WINDOW(window), 0);

    return FALSE;
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    GtkWidget* window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_container_set_border_width(GTK_CONTAINER(window), 12);

    gtk_layer_init_for_window(GTK_WINDOW(window));
    gtk_layer_set_anchor(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_BOTTOM, TRUE);
    gtk_layer_set_anchor(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_LEFT, TRUE);
    gtk_layer_set_anchor(GTK_WINDOW(window), GTK_LAYER_SHELL_EDGE_RIGHT, TRUE);

    GtkWidget *label = gtk_label_new("Test");
    gtk_container_add(GTK_CONTAINER(window), label);
    
    gtk_widget_show(window);
    gtk_widget_show_all(window);

    gtk_layer_auto_exclusive_zone_enable(GTK_WINDOW(window));

    g_timeout_add(300, timeout, window);

    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    gtk_main();

    return 0;
}
