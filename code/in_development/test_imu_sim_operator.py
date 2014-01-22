import bpy
import glob
import os
import sys
from queue import Queue, Empty
from threading import Thread

dirname = os.path.dirname

q = Queue()

path_to_this_file = dirname(dirname(os.path.realpath(__file__)))

#Imports blender_caller.py
sys.path.insert(0, path_to_this_file)
import blender_caller

def read_most_recent_run():
    f = open(path_to_this_file + os.sep +'mmr', 'r')
    mmr = f.read() + os.sep
    f.close()
    return mmr

scene = bpy.context.scene

class ModalOperator(bpy.types.Operator):
    """Get input from graph."""
    bl_idname = "object.test_imu_sim_operator"
    bl_label = "Test IMUSim Operator"
        
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
                if str(line.strip()) == "b'success!'":
                    return self.cancel(context)

                print(line)
                # Move the animation to the desired frame.
                # scene.frame_current = int(float(line))
                # bpy.ops.object.mode_set(mode='EDIT')
                # bpy.ops.object.mode_set(mode='OBJECT')
                # bpy.ops.render.render()
                # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Get the files ending with .csv extension.
        most_recent_run = read_most_recent_run() + 'raw'
        print ("MRR: " + most_recent_run)
        sensor_files = glob.glob(os.path.realpath(most_recent_run) + os.sep + '*csv')

        print(sensor_files)
        self._pipe = blender_caller.run_imu_sims(sensor_files)

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
    bpy.utils.register_class(ModalOperator)

def unregister():
    bpy.utils.unregister_class(ModalOperator)

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


if __name__ == "__main__":
    register()
