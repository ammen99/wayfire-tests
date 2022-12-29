#!/bin/env python3

import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

# A test to check that implicit grab works with tablet input
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'tablet')
        self.wait_for_clients(2)
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'tablet')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        layout['gtk2'] = (100, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        gtk1.reset_logs()
        gtk2.reset_logs()

        try:
            # Go to gtk1 and start implicit grab
            self.socket.tablet_tool_proximity(50, 50, True)
            self.wait_for_clients(2)

            gtk1.expect_line_throw("tool-proximity-in")
            gtk1.expect_line_throw("tool-motion 50,50")
            gtk1.expect_none_throw("(after prox in)")

            self.socket.tablet_tool_tip(50, 50, True)
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-down")
            gtk1.expect_line_throw("pad-enter") # gtk2 was focused as it is opened later
            gtk1.expect_none_throw("(after tool down)")
            gtk2.expect_line_throw("pad-leave")

            self.socket.tablet_tool_axis(150, 50, 0.1)
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-motion 150,50")
            gtk1.expect_line_throw("tool-pressure 6553")
            gtk1.expect_none_throw("(after motion)")
            gtk2.expect_none_throw("(after motion)")


            # Release implicit grab => gtk2 should get focus now
            self.socket.tablet_tool_tip(150, 50, False)
            self.wait_for_clients(2)
            gtk1.expect_line_throw("tool-up")
            gtk1.expect_line_throw("tool-proximity-out")
            gtk1.expect_none_throw("(after tip up)")

            gtk2.expect_line_throw("tool-proximity-in")
            gtk2.expect_line_throw("tool-motion 50,50")
            gtk2.expect_none_throw("(after tip up)")
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
