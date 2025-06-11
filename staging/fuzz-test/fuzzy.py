from wayfire import WayfireSocket
from random import choice, randint, random, sample
import threading
import time
import logging
from subprocess import Popen, PIPE, run
from wayfire.extra.ipc_utils import WayfireUtils
from wayfire.extra.stipc import Stipc


class TestWayfire:
    def __init__(self):
        self.sock = WayfireSocket()
        self.utils = WayfireUtils(self.sock)
        self.stipc = Stipc(self.sock)
        # Configure logging
        logging.basicConfig(
            filename="/tmp/wayfire-tests.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging
        self.logger.info("Starting test_wayfire execution.")
        # Map macro IDs to actions for log parsing / script generation
        self.macro_map = {
            "MOVE_CURSOR": "self.stipc.move_cursor",
            "CLICK_BUTTON": "self.stipc.click_button",
            "PRESS_KEY": "self.stipc.press_key",
            "SET_VIEW_MAXIMIZED": "self.utils.set_view_maximized",
            "SET_VIEW_FULLSCREEN": "self.sock.set_view_fullscreen",
            "SET_VIEW_MINIMIZED": "self.sock.set_view_minimized",
            "SET_VIEW_STICKY": "self.sock.set_view_sticky",
            "SEND_VIEW_TO_BACK": "self.sock.send_view_to_back",
            "SET_VIEW_ALPHA": "self.sock.set_view_alpha",
            "SET_VIEW_TOP_LEFT": "self.utils.set_view_top_left",
            "SET_VIEW_TOP_RIGHT": "self.utils.set_view_top_right",
            "SET_VIEW_BOTTOM_LEFT": "self.utils.set_view_bottom_left",
            "SET_VIEW_RIGHT": "self.utils.set_view_right",
            "SET_VIEW_LEFT": "self.utils.set_view_left",
            "SET_VIEW_BOTTOM": "self.utils.set_view_bottom",
            "SET_VIEW_TOP": "self.utils.set_view_top",
            "SET_VIEW_CENTER": "self.utils.set_view_center",
            "SET_VIEW_BOTTOM_RIGHT": "self.utils.set_view_bottom_right",
            "SET_FOCUS": "self.sock.set_focus",
            "CUBE_ACTIVATE": "self.sock.cube_activate",
            "CUBE_ROTATE_LEFT": "self.sock.cube_rotate_left",
            "CUBE_ROTATE_RIGHT": "self.sock.cube_rotate_right",
            "TOGGLE_EXPO": "self.sock.toggle_expo",
            "SCALE_TOGGLE": "self.sock.scale_toggle",
            "TOGGLE_SHOWDESKTOP": "self.sock.toggle_showdesktop",
            "CREATE_WAYLAND_OUTPUT": "self.stipc.create_wayland_output",
            "DESTROY_WAYLAND_OUTPUT": "self.stipc.destroy_wayland_output",
            "RUN_CMD": "self.stipc.run_cmd",
            "DELAY_NEXT_TX": "self.stipc.delay_next_tx",
            "GO_WORKSPACE_SET_FOCUS": "self.utils.go_workspace_set_focus",
            "CONFIGURE_VIEW": "self.sock.configure_view",
            "SET_WORKSPACE": "self.sock.set_workspace",
        }

    def test_random_press_key_with_modifiers(self, num_combinations=1):
        """
        Randomly generates key combinations and calls press_key function.

        Args:
            num_combinations (int): Number of random key combinations to generate.

        Returns:
            None
        """
        keys = [
            "KEY_CANCEL",
            "KEY_HELP",
            "KEY_BACK_SPACE",
            "KEY_TAB",
            "KEY_CLEAR",
            "KEY_ENTER",
            "KEY_SHIFT",
            "KEY_CONTROL",
            "KEY_ALT",
            "KEY_PAUSE",
            "KEY_CAPS_LOCK",
            "KEY_ESCAPE",
            "KEY_SPACE",
            "KEY_PAGE_UP",
            "KEY_PAGE_DOWN",
            "KEY_END",
            "KEY_HOME",
            "KEY_ARROW_LEFT",
            "KEY_ARROW_UP",
            "KEY_ARROW_RIGHT",
            "KEY_ARROW_DOWN",
            "KEY_PRINT_SCREEN",
            "KEY_INSERT",
            "KEY_DELETE",
            "KEY_0",
            "KEY_1",
            "KEY_2",
            "KEY_3",
            "KEY_4",
            "KEY_5",
            "KEY_6",
            "KEY_7",
            "KEY_8",
            "KEY_9",
            "KEY_SEMICOLON",
            "KEY_EQUALS",
            "KEY_A",
            "KEY_B",
            "KEY_C",
            "KEY_D",
            "KEY_E",
            "KEY_F",
            "KEY_G",
            "KEY_H",
            "KEY_I",
            "KEY_J",
            "KEY_K",
            "KEY_L",
            "KEY_M",
            "KEY_N",
            "KEY_O",
            "KEY_P",
            "KEY_Q",
            "KEY_R",
            "KEY_S",
            "KEY_T",
            "KEY_U",
            "KEY_V",
            "KEY_W",
            "KEY_X",
            "KEY_Y",
            "KEY_Z",
            "KEY_LEFT_WINDOW_KEY",
            "KEY_RIGHT_WINDOW_KEY",
            "KEY_SELECT_KEY",
            "KEY_NUMPAD_0",
            "KEY_NUMPAD_1",
            "KEY_NUMPAD_2",
            "KEY_NUMPAD_3",
            "KEY_NUMPAD_4",
            "KEY_NUMPAD_5",
            "KEY_NUMPAD_6",
            "KEY_NUMPAD_7",
            "KEY_NUMPAD_8",
            "KEY_NUMPAD_9",
            "KEY_MULTIPLY",
            "KEY_ADD",
            "KEY_SEPARATOR",
            "KEY_SUBTRACT",
            "KEY_DECIMAL_POINT",
            "KEY_DIVIDE",
            "KEY_F1",
            "KEY_F2",
            "KEY_F3",
            "KEY_F4",
            "KEY_F5",
            "KEY_F6",
            "KEY_F7",
            "KEY_F8",
            "KEY_F9",
            "KEY_F10",
            "KEY_F11",
            "KEY_F12",
            "KEY_NUM_LOCK",
            "KEY_SCROLL_LOCK",
            "KEY_COMMA",
            "KEY_PERIOD",
            "KEY_SLASH",
            "KEY_BACK_QUOTE",
            "KEY_OPEN_BRACKET",
            "KEY_BACK_SLASH",
            "KEY_CLOSE_BRACKET",
            "KEY_QUOTE",
            "KEY_META",
        ]

        modifiers = ["A-", "S-", "C-"]

        for _ in range(num_combinations):
            modifier = choice(modifiers)
            main_key = choice(keys)
            key_combination = modifier + main_key
            try:
                self.logger.info(f"press_key {key_combination} [macro_id=PRESS_KEY]")
                self.stipc.press_key(key_combination)
            except Exception as e:
                continue

    def test_random_set_view_position(self, view_id):
        if view_id is None:
            view_id = self.test_random_view_id()

        if view_id:

            def set_position(position, view_id=view_id):
                self.logger.info(
                    f"Setting position: {position} [macro_id=SET_VIEW_{position.upper().replace(' ', '_')}]"
                )
                if position == "top_left":
                    self.utils.set_view_top_left(view_id)
                elif position == "top_right":
                    self.utils.set_view_top_right(view_id)
                elif position == "bottom_left":
                    self.utils.set_view_bottom_left(view_id)
                elif position == "right":
                    self.utils.set_view_right(view_id)
                elif position == "left":
                    self.utils.set_view_left(view_id)
                elif position == "bottom":
                    self.utils.set_view_bottom(view_id)
                elif position == "top":
                    self.utils.set_view_top(view_id)
                elif position == "center":
                    self.utils.set_view_center(view_id)
                elif position == "bottom_right":
                    self.utils.set_view_bottom_right(view_id)

            actions = [
                lambda: set_position("top_left"),
                lambda: set_position("top_right"),
                lambda: set_position("bottom_left"),
                lambda: set_position("right"),
                lambda: set_position("left"),
                lambda: set_position("bottom"),
                lambda: set_position("top"),
                lambda: set_position("center"),
                lambda: set_position("bottom_right"),
            ]
            action = choice(actions)
            action()

    def test_random_change_view_state(self, view_id):
        def view_state(action, view_id=view_id):
            if action == "set_view_maximized":
                self.logger.info(
                    f"set_view_maximized: {view_id} [macro_id=SET_VIEW_MAXIMIZED]"
                )
                self.utils.set_view_maximized(view_id)
            if action == "set_view_fullscreen":
                self.logger.info(
                    f"set_view_fullscreen: {view_id} [macro_id=SET_VIEW_FULLSCREEN]"
                )
                self.sock.set_view_fullscreen(view_id, True)
            if action == "set_view_miminized":
                self.logger.info(
                    f"set_view_miminized: {view_id} [macro_id=SET_VIEW_MINIMIZED]"
                )
                self.sock.set_view_minimized(view_id, True)
            if action == "set_view_miminized":
                self.logger.info(
                    f"set_view_minimized: {view_id} [macro_id=SET_VIEW_MINIMIZED]"
                )
                self.sock.set_view_minimized(view_id, False)
            if action == "set_view_sticky":
                self.logger.info(
                    f"set_view_sticky: {view_id} [macro_id=SET_VIEW_STICKY]"
                )
                self.sock.set_view_sticky(view_id, choice([True, False]))
            if action == "send_view_to_back":
                self.logger.info(
                    f"send_view_to_back: {view_id} [macro_id=SEND_VIEW_TO_BACK]"
                )
                self.sock.send_view_to_back(view_id, choice([True, False]))
            if action == "set_view_alpha":
                self.logger.info(f"set_view_alpha: {view_id} [macro_id=SET_VIEW_ALPHA]")
                self.sock.set_view_alpha(view_id, random() * 1.0)

        if view_id is not None:
            view_id = self.test_random_view_id()
            if view_id:
                actions = [
                    lambda: view_state("set_view_maximized"),
                    lambda: view_state("set_view_fullscreen"),
                    lambda: view_state("set_view_minimized"),
                    lambda: view_state("set_view_minimized"),
                    lambda: view_state("set_view_sticky"),
                    lambda: view_state("send_view_to_back"),
                    lambda: view_state("set_view_alpha"),
                ]
                action = choice(actions)
                action()

    def test_random_list_info(self, view_id):
        if view_id is None:
            view_id = self.test_random_view_id()

        if view_id:

            def socket_action(action, view_id=view_id):
                if action == "wset_info":
                    self.logger.info(f"wset_info: {view_id}")
                    self.sock.wset_info(view_id)
                elif action == "get_view":
                    self.logger.info(f"get_view: {view_id}")
                    self.sock.get_view(view_id)
                elif action == "get_view_alpha":
                    self.logger.info(f"get_view_alpha: {view_id}")
                    self.sock.get_view_alpha(view_id)

            actions = [
                lambda: self.sock.list_outputs(),
                lambda: self.sock.list_wsets(),
                lambda: socket_action("wset_info"),
                lambda: socket_action("get_view"),
                lambda: socket_action("get_view_alpha"),
                lambda: self.sock.list_input_devices(),
                lambda: self.utils.get_workspaces_with_views(),
                lambda: self.utils.get_workspaces_without_views(),
                lambda: self.utils.get_views_from_active_workspace(),
            ]

            action = choice(actions)
            action()

    def test_set_view_position(self, view_id):
        if view_id is None:
            view_id = self.test_random_view_id()
        if isinstance(view_id, int):
            self.logger.info(f"set_view_top_left: {view_id}")
            self.utils.set_view_top_left(view_id)
            self.logger.info(f"set_view_top_right: {view_id}")
            self.utils.set_view_top_right(view_id)
            self.logger.info(f"set_view_bottom_left: {view_id}")
            self.utils.set_view_bottom_left(view_id)
            self.logger.info(f"set_view_right: {view_id}")
            self.utils.set_view_right(view_id)
            self.logger.info(f"set_view_left: {view_id}")
            self.utils.set_view_left(view_id)
            self.logger.info(f"set_view_bottom: {view_id}")
            self.utils.set_view_bottom(view_id)
            self.logger.info(f"set_view_top: {view_id}")
            self.utils.set_view_top(view_id)
            self.logger.info(f"set_view_center: {view_id}")
            self.utils.set_view_center(view_id)
            self.logger.info(f"set_view_bottom_right: {view_id}")
            self.utils.set_view_bottom_right(view_id)
            self.logger.info(f"set_focus: {view_id}")
            self.sock.set_focus(view_id)

    def test_random_view_id(self):
        ids = self.utils.list_ids()
        if ids:
            return choice(ids)

    def test_change_view_state(self, view_id):
        if view_id is None:
            view_id = self.test_random_view_id()
        if isinstance(view_id, int):

            def socket_actions(action, view_id=view_id):
                if action == "maximize":
                    self.logger.info(
                        f"Maximizing: {view_id} [macro_id=SET_VIEW_MAXIMIZED]"
                    )
                    self.utils.set_view_maximized(view_id)
                elif action == "fullscreen":
                    self.logger.info(
                        f"Fullscreen: {view_id} [macro_id=SET_VIEW_FULLSCREEN]"
                    )
                    self.sock.set_view_fullscreen(view_id, True)
                elif action == "minimize":
                    val = choice([True, False])
                    self.logger.info(
                        f"Minimize ({val}): {view_id} [macro_id=SET_VIEW_MINIMIZED]"
                    )
                    self.sock.set_view_minimized(view_id, val)
                elif action == "sticky":
                    val = choice([True, False])
                    self.logger.info(
                        f"Sticky ({val}): {view_id} [macro_id=SET_VIEW_STICKY]"
                    )
                    self.sock.set_view_sticky(view_id, val)
                elif action == "send_back":
                    val = choice([True, False])
                    self.logger.info(
                        f"Send to back ({val}): {view_id} [macro_id=SEND_VIEW_TO_BACK]"
                    )
                    self.sock.send_view_to_back(view_id, val)
                elif action == "alpha":
                    alpha = random() * 1.0
                    self.logger.info(
                        f"Set alpha ({alpha:.2f}): {view_id} [macro_id=SET_VIEW_ALPHA]"
                    )
                    self.sock.set_view_alpha(view_id, alpha)

            actions = [
                lambda: socket_actions("maximize"),
                lambda: socket_actions("fullscreen"),
                lambda: socket_actions("minimize"),
                lambda: socket_actions("sticky"),
                lambda: socket_actions("send_back"),
                lambda: socket_actions("alpha"),
            ]
            action = choice(actions)
            action()

    def test_move_cursor_and_click(self):
        sumgeo = self.utils._sum_geometry_resolution()
        x, y = randint(100, sumgeo[0]), randint(100, sumgeo[0])
        self.logger.info(f"move_cursor: {x, y} [macro_id=MOVE_CURSOR]")
        self.stipc.move_cursor(x, y)
        self.logger.info("click_button: BTN_LEFT full [macro_id=CLICK_BUTTON]")
        self.stipc.click_button("BTN_LEFT", "full")

    def test_move_cursor_and_drag_drop(self):
        sumgeo = self.utils._sum_geometry_resolution()
        random_iterations = randint(1, 8)

        for _ in range(random_iterations):
            self.logger.info("click_and_drag: S-BTN_LEFT [macro_id=CLICK_AND_DRAG]")
            self.stipc.click_and_drag(
                "S-BTN_LEFT",
                randint(1, sumgeo[0]),
                randint(1, sumgeo[1]),
                randint(1, sumgeo[0]),
                randint(1, sumgeo[1]),
                True,
            )

    def test_list_info(self, view_id):
        if view_id is None:
            view_id = self.test_random_view_id()

        self.logger.info("list outputs")
        self.sock.list_outputs()
        self.logger.info("list wsets")
        self.sock.list_wsets()

        if isinstance(view_id, int):
            self.logger.info(f"get_view {view_id}")
            self.sock.get_view(view_id)
            self.logger.info(f"get_view {view_id}")
            self.sock.get_view(view_id)
            self.logger.info(f"get_view {view_id}")
            self.sock.get_view_alpha(view_id)
            self.logger.info(f"get_view_alpha {view_id}")
            self.sock.set_focus(view_id)
            self.logger.info(f"set_focus: {view_id}")

        self.logger.info("listing input devices")
        self.sock.list_input_devices()
        self.logger.info("get workspaces with views")
        self.utils.get_workspaces_with_views()
        self.logger.info("get workspaces without views")
        self.utils.get_workspaces_without_views()
        self.logger.info("get views from active workspace")
        self.utils.get_views_from_active_workspace()

    def test_cube_plugin(self):
        self.logger.info("plugin: cube activate [macro_id=CUBE_ACTIVATE]")
        self.sock.cube_activate()
        self.logger.info("plugin: cube rotate_left [macro_id=CUBE_ROTATE_LEFT]")
        self.sock.cube_rotate_left()
        self.logger.info("plugin: cube rotate_right [macro_id=CUBE_ROTATE_RIGHT]")
        self.sock.cube_rotate_right()
        self.logger.info("click BTN_LEFT inside plugin cube [macro_id=CLICK_BUTTON]")
        self.stipc.click_button("BTN_LEFT", "full")

    def test_toggle_switcher_view_plugin(self):
        for _ in range(2):
            self.stipc.press_key("A-KEY_TAB")

    def test_toggle_tile_plugin(self):
        self.stipc.press_key("W-KEY_T")

    def test_auto_rotate_plugin(self):
        keys_combinations = [
            "C-W-KEY_UP",
            "C-W-KEY_LEFT",
            "C-W-KEY_RIGHT",
            "C-W-KEY_DOWN",
        ]

        for _ in range(len(keys_combinations)):
            key_combination = choice(keys_combinations)
            self.logger.info(f"plugin auto rotate: press_key {key_combination}")
            self.stipc.press_key(key_combination)

    def test_invert_plugin(self):
        for _ in range(2):
            self.stipc.press_key("A-KEY_I")

    def test_magnifier_plugin(self):
        for _ in range(2):
            self.stipc.press_key("A-W-KEY_M")

    def test_focus_change_plugin(self):
        for _ in range(2):
            self.stipc.press_key("S-W-KEY_UP")
            self.stipc.press_key("S-W-KEY_DOWN")
            self.stipc.press_key("S-W-KEY_LEFT")
            self.stipc.press_key("S-W-KEY_RIGHT")

    def test_output_switcher_plugin(self):
        for _ in range(2):
            self.stipc.press_key("A-KEY_O")
            self.stipc.press_key("A-S-KEY_O")

    def test_low_priority_plugins(self, plugin=None):
        def plugin_action(name):
            if name == "invert":
                self.logger.info("Testing Invert Plugin [macro_id=PRESS_KEY]")
                self.test_invert_plugin()
            elif name == "focus-change":
                self.logger.info("Testing Focus Change Plugin [macro_id=PRESS_KEY]")
                self.test_focus_change_plugin()
            elif name == "magnifier":
                self.logger.info("Testing Magnifier Plugin [macro_id=PRESS_KEY]")
                self.test_magnifier_plugin()
            elif name == "output-switcher":
                self.logger.info("Testing Output Switcher Plugin [macro_id=PRESS_KEY]")
                self.test_output_switcher_plugin()

        actions = [
            lambda: plugin_action("invert"),
            lambda: plugin_action("focus-change"),
            lambda: plugin_action("magnifier"),
            lambda: plugin_action("output-switcher"),
        ]
        if plugin is None:
            action = choice(actions)
            action()
        elif plugin in ["invert", "focus-change", "magnifier", "output-switcher"]:
            plugin_action(plugin)

    def test_plugins(self, plugin=None):
        def plugin_action(action_name):
            if action_name == "expo":
                self.logger.info("Toggling Expo [macro_id=TOGGLE_EXPO]")
                self.sock.toggle_expo()
            elif action_name == "scale":
                self.logger.info("Toggling Scale [macro_id=SCALE_TOGGLE]")
                self.sock.scale_toggle()
            elif action_name == "showdesktop":
                self.logger.info("Toggling Show Desktop [macro_id=TOGGLE_SHOWDESKTOP]")
                self.sock.toggle_showdesktop()
            elif action_name == "cube":
                self.logger.info("Testing Cube Plugin [macro_id=CUBE_ACTIVATE]")
                self.test_cube_plugin()
            elif action_name == "switcherview":
                self.logger.info("Testing Switcher View Plugin [macro_id=CLICK_BUTTON]")
                self.test_toggle_switcher_view_plugin()
            elif action_name == "autorotate":
                self.logger.info("Testing Auto Rotate Plugin [macro_id=PRESS_KEY]")
                self.test_auto_rotate_plugin()
            elif action_name == "invert":
                self.logger.info("Testing Invert Plugin [macro_id=PRESS_KEY]")
                self.test_invert_plugin()
            elif action_name == "tile":
                self.logger.info("Testing Tile Plugin [macro_id=PRESS_KEY]")
                self.test_toggle_tile_plugin()

        actions = [
            lambda: plugin_action("expo"),
            lambda: plugin_action("scale"),
            lambda: plugin_action("showdesktop"),
            lambda: plugin_action("cube"),
            lambda: plugin_action("switcherview"),
            lambda: plugin_action("autorotate"),
            lambda: plugin_action("invert"),
            lambda: plugin_action("tile"),
        ]
        if plugin is None:
            action = choice(actions)
            action()
        else:
            if plugin in [  # safeguard to avoid errors
                "expo",
                "scale",
                "showdesktop",
                "cube",
                "switcherview",
                "autorotate",
                "invert",
                "tile",
            ]:
                plugin_action(plugin)

    def test_output(self):
        current_outputs = self.utils.list_outputs_ids()
        self.logger.info("create_wayland_output() [macro_id=CREATE_WAYLAND_OUTPUT]")
        if randint(1, 99) != 4:
            return
        self.stipc.create_wayland_output()
        for output_id in self.utils.list_outputs_ids():
            if output_id in current_outputs:
                continue
            else:
                name = self.utils.get_output_name_by_id(output_id)
                if name and False:
                    self.logger.info(
                        f"destroy_wayland_output {name} [macro_id=DESTROY_WAYLAND_OUTPUT]"
                    )
                    self.stipc.destroy_wayland_output(name)

    def test_is_terminal_available(self, terminal):
        try:
            Popen(["which", terminal], stdout=PIPE, stderr=PIPE)
            return True
        except FileNotFoundError:
            return False

    def test_choose_terminal(self):
        terminals = [
            "xterm",
            "alacritty",
            "kitty",
            "rxvt",
            "rxvt-unicode",
            "lxterminal",
            "eterm",
            "roxterm",
            "mlterm",
            "sakura",
            "aterm",
            "xfce4-terminal",
            "mlterm",
            "stterm",
            "konsole",
            "gnome-terminal",
            "mate-terminal",
            "terminology",
            "terminator",
            "tilda",
            "tilix",
            "alacritty",
            "foot",
            "cool-retro-term",
            "deepin-terminal",
            "rxvt-unicode-256color",
            "pantheon-terminal",
        ]
        for terminal in terminals:
            if self.test_is_terminal_available(terminal):
                self.logger.info(f"run terminal: {terminal}")
                run(["killall", "-9", terminal])
                return terminal
        return None

    def test_spam_terminals(self, number_of_views_to_open, wayland_display=None):
        chosen_terminal = self.test_choose_terminal()
        if chosen_terminal:
            for _ in range(number_of_views_to_open):
                if wayland_display is None:
                    self.logger.info(f"run_cmd {chosen_terminal} [macro_id=RUN_CMD]")
                    self.stipc.run_cmd(chosen_terminal)
                else:
                    command = "export WAYLAND_DISPLAY={0} ; {1}".format(
                        wayland_display, chosen_terminal
                    )
                    Popen(command, shell=True)

    def test_spam_go_workspace_set_focus(self):
        list_ids = self.utils.list_ids()
        num_items = randint(1, len(list_ids))
        random_views = sample(list_ids, num_items)
        for view_id in random_views:
            self.logger.info(
                f"go_workspace_set_focus: {view_id} [macro_id=GO_WORKSPACE_SET_FOCUS]"
            )
            self.utils.go_workspace_set_focus(view_id)

    def test_set_function_priority(self, functions):
        priority = []
        for _ in range(randint(1, 4)):
            action = choice(functions)
            priority.append(action)
        return priority

    def random_delay_next_tx(self):
        random_run = randint(1, 8)
        if random_run > 4:
            for _ in range(1, randint(2, 100)):
                self.stipc.delay_next_tx()

    def test_random_views(self, view_id):
        functions = [
            lambda: self.test_random_set_view_position(view_id),
            lambda: self.test_random_change_view_state(view_id),
            lambda: self.test_set_view_position(view_id),
            lambda: self.test_change_view_state(view_id),
        ]

        action = choice(functions)
        action()

    def test_wayfire(
        self, number_of_views_to_open, max_tries=1, speed=0, plugin=None, display=None
    ):
        from gtk3_window import spam_new_views
        from gtk3_dialogs import spam_new_dialogs

        # Retrieve necessary data
        view_id = self.test_random_view_id()
        workspaces = (
            [{"x": x, "y": y} for x, y in self.utils._total_workspaces().values()]
            if self.utils._total_workspaces()
            else []
        )
        sumgeo = self.utils._sum_geometry_resolution()
        # Define functions to be executed
        functions = [
            (self.utils.go_workspace_set_focus, (view_id)),
            (self.test_move_cursor_and_click, ()),
            (self.test_plugins, (plugin,)),
            (self.test_low_priority_plugins, (plugin,)),
            (self.test_move_cursor_and_drag_drop, ()),
            (self.test_output, ()),
            (self.test_random_views, (view_id)),
            (
                self.sock.configure_view,
                (
                    view_id,
                    randint(1, sumgeo[0]),
                    randint(0, sumgeo[1]),
                    randint(1, sumgeo[0]),
                    randint(1, sumgeo[1]),
                ),
            ),
            (
                self.sock.set_workspace,
                (choice(workspaces), view_id, choice(self.utils.list_outputs_ids())),
            ),
        ]
        iterations = 0
        self.test_spam_terminals(number_of_views_to_open, wayland_display=display)

        # Start spamming views
        thread = threading.Thread(target=spam_new_views)
        thread.start()
        thread = threading.Thread(target=spam_new_dialogs)
        thread.start()

        # spam_new_layers_thread = threading.Thread(target=spam_new_layers)
        # spam_new_layers_thread.start()

        # FIXME: Implement this to not use keybinds in the terminal with script running
        # first_view_focused = self.get_focused_view()

        # Execute functions with specified priority
        self.test_set_function_priority(functions)
        should_execute_function_priority = 0
        should_change_function_priority = 0

        while iterations < max_tries:
            if speed != 0:
                random_time = speed / randint(1, speed)
                time.sleep(random_time / 1000)
            try:
                # Repeat certain functions every N iterations
                if should_execute_function_priority > 20:
                    should_execute_function_priority = 0
                should_execute_function_priority += 1
                if should_change_function_priority > 40:
                    self.test_set_function_priority(functions)
                    should_execute_function_priority = 0
                should_change_function_priority += 1
                random_function, args = choice(functions)
                random_function(*args)
                iterations += 1
                self.random_delay_next_tx()

                if iterations + 1 == max_tries and False:
                    # lets close the focused output in the last iteration
                    # so it closes while still there are actions going on
                    try:
                        output_id = self.utils.get_focused_output_id()
                        if output_id:
                            name = self.utils.get_output_name_by_id(output_id)
                            if name:
                                self.stipc.destroy_wayland_output(name)
                    except:
                        pass

            except:
                self.test_set_function_priority(functions)
