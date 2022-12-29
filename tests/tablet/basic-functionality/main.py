import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

# A test to check that Wayfire correctly sends the various tablet events
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'tablet')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Go to gtk1 and start implicit grab
        try:
            gtk1.expect_line_throw("pad-enter")
            self.socket.tablet_pad_button(23, True)
            self.socket.tablet_pad_button(23, False)
            self.wait_for_clients(2)
            gtk1.expect_line_throw("pad-button-press 23")
            gtk1.expect_line_throw("pad-button-release 23")

            self.socket.tablet_tool_proximity(10, 10, True);
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-proximity-in")

            self.socket.tablet_tool_tip(10, 10, True);
            self.socket.tablet_tool_axis(15, 10, 0.1);
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-motion 10,10")
            gtk1.expect_line_throw("tool-down")
            gtk1.expect_line_throw("tool-motion 15,10")
            gtk1.expect_line_throw("tool-pressure 6553")

            self.socket.tablet_tool_button(24, True)
            self.socket.tablet_tool_button(24, False)
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-button-press 24")
            gtk1.expect_line_throw("tool-button-release 24")

            self.socket.tablet_tool_tip(0, 0, False);
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-up")

            self.socket.tablet_tool_proximity(10, 10, False);
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-proximity-out")

            gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'tablet')
            self.wait_for_clients(2)
            gtk1.expect_line_throw("pad-leave")
            gtk2.expect_line_throw("pad-enter")
            gtk1.expect_none_throw()
            gtk2.expect_none_throw()

        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
