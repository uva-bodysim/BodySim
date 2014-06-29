_modules = [
    "file_operations",
    "plugins_info",
    "current_sensors_panel",
    "graph_operator",
    "message_operators",
    "sensor_addition",
    "sensor_operators",
    "simtools_panel"
]

import bpy

__import__(name=__name__, fromlist=_modules)
_namespace = globals()
_modules_loaded = {name: _namespace[name] for name in _modules if name != 'bpy'}
del _namespace


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
