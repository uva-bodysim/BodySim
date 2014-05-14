"""
A modal operator in blender that takes cursor data from the plotter and moves
the animation to the desired time. Implementation is non-blocking so blender
does not freeze while it is running. See wiki for more details.
"""

import bpy
import glob
import os
import sys
from queue import Queue, Empty
from threading import Thread
from vertex_group_operator import get_plugins

dirname = os.path.dirname
path_to_this_file = dirname(dirname(os.path.realpath(__file__)))
q = Queue()

#Imports blender_caller.py
sys.path.insert(0, dirname(dirname(__file__)))
import blender_caller

scene = bpy.context.scene

class GraphOperator(bpy.types.Operator):
    """Get input from graph."""
    bl_idname = "bodysim.graph"
    bl_label = "Graph Modal Operator"
    plot_type = bpy.props.StringProperty()    
    _timer = None
    _pipe = None
    _thread = None

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            try:
                line = q.get_nowait()
            except Empty:
                pass
            else:
                # Stop the operator if the graph window is closed.
                if str(line.strip()) == "b'quit'":
                    return self.cancel(context)

                # Move the animation to the desired frame.
                scene.frame_current = int(float(line))
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.render.render()
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Get the files ending with .csv extension.'
        model = context.scene.objects['model']
        curr_sim_path = model['current_simulation_path']

        # Graphing: one tab per sensor. One plot per unit group per plugin.
        plugins_tuple = get_plugins(path_to_this_file, False)
        graph_var_map = {}
        for sensor in model['sensor_info']:
            for plugin in plugins_tuple[0]:
                for variable in plugins_tuple[0][plugin]['variables']:
                    if getattr(context.scene.objects['sensor_' + sensor], 'GRAPH_' +  plugin + variable):
                        if sensor not in graph_var_map:
                            graph_var_map[sensor] = {}

                        if plugin not in graph_var_map[sensor]:
                            graph_var_map[sensor][plugin] = {}

                        curr_var = plugin + variable
                        curr_pair = None
                        for unit_pair in plugins_tuple[1]:
                            if curr_var in plugins_tuple[1][unit_pair]:
                                curr_pair = unit_pair
                                break

                        if curr_pair not in graph_var_map[sensor][plugin]:
                            graph_var_map[sensor][plugin][curr_pair] = []

                        graph_var_map[sensor][plugin][curr_pair].append((variable, plugins_tuple[0][plugin]['variables'].index(variable)))

        self._pipe = blender_caller.plot_csv(str(30), curr_sim_path, graph_var_map)
        
        # A separate thread must be started to keep track of the blocking pipe
        # so the script does not freeze blender.
        self._thread = Thread(target=enqueue_output, args=(self._pipe.stdout, q))
        self._thread.daemon = True
        self._thread.start()
        self._timer = context.window_manager.event_timer_add(0.2, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}

def register():
    bpy.utils.register_class(GraphOperator)

def unregister():
    bpy.utils.unregister_class(GraphOperator)

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


if __name__ == "__main__":
    register()
