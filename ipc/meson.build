project(
	'wayfire-smoke-tests-ipc',
    'c',
	'cpp',
	version: '0.0',
	license: 'MIT',
	meson_version: '>=0.51.0',
	default_options: [
		'cpp_std=c++17',
        'c_std=c11',
		'warning_level=2',
		'werror=false',
	],
)

wayfire  = dependency('wayfire')
wlroots  = dependency('wlroots')
wfconfig = dependency('wf-config')
json     = subproject('json').get_variable('nlohmann_json_dep')

add_project_arguments(['-DWLR_USE_UNSTABLE'], language: ['cpp', 'c'])
add_project_arguments(['-DWAYFIRE_PLUGIN'], language: ['cpp', 'c'])
add_project_link_arguments(['-rdynamic'], language:'cpp')

pms = shared_module('wfst-ipc', ['ipc.cpp', 'plugin.cpp'],
    dependencies: [wayfire, wlroots, wfconfig, json],
    install: true, install_dir: wayfire.get_variable(pkgconfig: 'plugindir'))

summary = [
	'',
	'----------------',
	'wayfire-smoke-tests-ipc @0@'.format(meson.project_version()),
	'----------------',
	''
]
message('\n'.join(summary))
