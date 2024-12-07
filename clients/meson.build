project(
	'wayfire',
	'c',
	'cpp',
	version: '0.8.0',
	license: 'MIT',
	meson_version: '>=0.58.0',
	default_options: [
		'cpp_std=c++17',
		'c_std=c11',
		'warning_level=2',
		'werror=false',
	],
)

# Dependencies
x11 = dependency('x11')
gtkmm = dependency('gtkmm-3.0')
cairo = dependency('cairo')
wayland_client = dependency('wayland-client')
wayland_protos = dependency('wayland-protocols', version: '>=1.12')
logger_inc = include_directories(['.'])
gtklayershell  = dependency('gtk-layer-shell-0', version: '>= 0.6')

# Custom wayland protocols needed
wl_protocol_dir = wayland_protos.get_variable('pkgdatadir')
wayland_scanner = find_program('wayland-scanner')

wayland_scanner_code = generator(
	wayland_scanner,
	output: '@BASENAME@-protocol.c',
	arguments: ['private-code', '@INPUT@', '@OUTPUT@'],
)

wayland_scanner_client = generator(
	wayland_scanner,
	output: '@BASENAME@-client-protocol.h',
	arguments: ['client-header', '@INPUT@', '@OUTPUT@'],
)

protocols = [
    [wl_protocol_dir, 'unstable/pointer-constraints/pointer-constraints-unstable-v1.xml'],
    [wl_protocol_dir, 'unstable/tablet/tablet-unstable-v2.xml'],
    [wl_protocol_dir, 'stable/xdg-shell/xdg-shell.xml'],
    ['wlr-foreign-toplevel-management-unstable-v1.xml']
]

wl_protos_src = []
wl_protos_headers = []

foreach p : protocols
	xml = join_paths(p)
	wl_protos_src += wayland_scanner_code.process(xml)
	wl_protos_headers += wayland_scanner_client.process(xml)
endforeach

lib_wl_protos = static_library('wl_protos', wl_protos_src + wl_protos_headers,
	dependencies: [wayland_client]) # for the include directory

wl_protos = declare_dependency(
	link_with: lib_wl_protos,
	sources: wl_protos_headers,
)

# Test clients
executable('x11_click_to_close', ['x11_click_to_close.cpp'],
    dependencies: x11,
    include_directories: logger_inc,
    install: false)

executable('x11_map_unmap', ['x11_map_unmap.cpp'],
    dependencies: x11,
    include_directories: logger_inc,
    install: false)

executable('x11_logger', ['x11_logger.cpp'],
    dependencies: x11,
    include_directories: logger_inc,
    install: false)

executable('gtk_special', ['gtk_special.cpp'],
    dependencies: gtkmm,
    include_directories: logger_inc,
    install: false)

executable('gtk_drag_and_drop', ['gtk_drag_and_drop.cpp'],
    dependencies: gtkmm,
    include_directories: logger_inc,
    install: false)

executable('gtk_logger', ['gtk_logger.cpp'],
    dependencies: [gtkmm, wayland_client, wl_protos],
    include_directories: logger_inc,
    install: false)

executable('gtk_color_switcher', ['gtk_color_switcher.cpp'],
    dependencies: [gtkmm],
    install: false)

executable('layer_shell_kb_popup', ['gtk_layer_shell_kb_popup.cpp'],
    dependencies: [gtkmm, gtklayershell],
    install: false)

executable('layer_shell_delay_exclusive', ['gtk_layer_delayed_exclusive.cpp'],
    dependencies: [gtkmm, gtklayershell],
    install: false)

executable('xdg_popup_crasher', ['xdg_popup_crasher.c'],
    dependencies: [cairo, wayland_client, wl_protos],
    install: false)

