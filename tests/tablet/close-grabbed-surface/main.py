import wfutil as wu
import wftest as wt
import os
import signal

def is_gui() -> bool:
    return False

# A test starts an implicit grab on one of the surfaces using tablet input and checks that wayfire doesn't crash
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'tablet')
        self.wait_for_clients(2)
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'tablet &> /tmp/g2')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        layout['gtk2'] = (100, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        try:
            # Go to gtk1 and start implicit grab
            self.socket.tablet_tool_proximity(50, 50, True)
            self.socket.tablet_tool_tip(50, 50, True)
            self.socket.tablet_tool_axis(150, 50, 0.1)
            self.wait_for_clients(2)
            gtk1.reset_logs()
            gtk2.reset_logs()

            self.send_signal(gtk1.pid, signal.SIGKILL)
            self.wait_for_clients(2)

            gtk1.expect_none_throw("(after kill)")
            self.socket.tablet_tool_tip(50, 50, False)

            gtk2.expect_unordered_lines_throw(["pad-enter", "tool-proximity-in", "tool-motion 50,50"])
            gtk2.expect_none_throw("(trailing)")
            self.wait_for_clients(2)
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        if self._get_views() != ['gtk2']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
