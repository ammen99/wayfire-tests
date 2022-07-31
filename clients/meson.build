project(
	'wayfire',
	'c',
	'cpp',
	version: '0.8.0',
	license: 'MIT',
	meson_version: '>=0.53.0',
	default_options: [
		'cpp_std=c++17',
		'c_std=c11',
		'warning_level=2',
		'werror=false',
	],
)

x11 = dependency('x11')
gtkmm = dependency('gtkmm-3.0')
wayland_client = dependency('wayland-client')
logger_inc = include_directories(['.'])

executable('x11_click_to_close', ['x11_click_to_close.cpp'],
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
    dependencies: [gtkmm, wayland_client],
    include_directories: logger_inc,
    install: false)
