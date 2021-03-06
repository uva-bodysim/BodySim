"""A modal operator in blender that takes cursor data from the plotter
 and moves the animation to the desired time. Implementation is
 non-blocking so blender does not freeze while it is running. See wiki
 for more details.

 NOTE: Simulators must output to a folder within the simulation folder
 with the exact same name as specified in the name attribute of the
 simulator element in plugins.xml.
"""

import bpy
from queue import Queue, Empty
from threading import Thread
import Bodysim.plugins_info
q = Queue()

import Bodysim.blender_caller

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
                scene = bpy.context.scene
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
        """Produce a dictionary holding information about what sensor
         data to be graphed and passes it to the plotter. Goes through
         each sensor and sees which variables it needs to plot, as
         well as what column in the csv log it can get data from.

         NOTE: Assuming that the columns that correspond to the logged
         variables are in the same order as specified in plugins.xml.
         The first column is reserved for the independent variable.
        """
        model = context.scene.objects['model']
        curr_sim_path = model['current_simulation_path']
        plugins_tuple = Bodysim.plugins_info.plugins_tuple
        graph_var_map = {}
        sim_dict = Bodysim.plugins_info.get_sensor_plugin_mapping()[0]
        for  sensor in model['sensor_info']:
            sensor_name = model['sensor_info'][sensor][0]
            for plugin in plugins_tuple[0]:
                for variable in plugins_tuple[0][plugin]['variables']:
                    if getattr(context.scene.objects['sensor_' + sensor], 'GRAPH_' +  plugin + variable):
                        if sensor_name not in graph_var_map:
                            graph_var_map[sensor_name] = {}

                        if plugin not in graph_var_map[sensor_name]:
                            graph_var_map[sensor_name][plugin] = {}

                        curr_var = plugin + variable
                        curr_pair = None
                        for unit_pair in plugins_tuple[1]:
                            if curr_var in plugins_tuple[1][unit_pair]:
                                curr_pair = unit_pair
                                break

                        if curr_pair not in graph_var_map[sensor_name][plugin]:
                            graph_var_map[sensor_name][plugin][curr_pair] = []

                        # The first column of the log is reserved for the independent variable.
                        graph_var_map[sensor_name][plugin][curr_pair].append((variable,
                                                                         sim_dict[sensor][plugin].index(variable) + 1))

        print(graph_var_map)
        self._pipe = Bodysim.blender_caller.plot_csv(str(30), curr_sim_path, graph_var_map)
        
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
