"""
Script that binds cubes to paths and prints the location of the cubes as they
move along the path to a file. Currently for use with the
sensor_to_path_tracking.blend file. See wiki for more details.
"""

import bpy
import os
import "../../blender_caller"

SCENE_NAME = bpy.context.scene.name
FRAME_START = 1
FRAME_END = 101
cubes = 3

scene = bpy.context.scene

# Set the overall number of frames in this scene
scene.frame_start = 1
scene.frame_end = 101

# Save in the same directory as the blend file
file_name = 'test'
dirname = os.path.dirname

# List of objects and files to write to
cube_objects = []
path_objects = []
data_files = []

def main():
    bind_to_path()
    track_cubes()

def bind_to_path():
    """Bind cubes to paths."""
    # Get the cubes and corresponding paths
    for i in range(cubes):
        cube_objects.append(bpy.data.objects["Cube_" + str(i)])
        path_objects.append(bpy.data.objects["NurbsPath_" + str(i)])

    # Bind cubes to corresponding path and animate paths
    for i in range(cubes):
        # Bind
        current_cube_constraint = \
            cube_objects[i].constraints.new(type='FOLLOW_PATH')
        current_cube_constraint.target = path_objects[i]
        current_cube_constraint.forward_axis = 'FORWARD_X'
        current_cube_constraint.use_curve_follow = True

        # Set location of cube center to be on the path
        cube_objects[i].location[0] = 0
        cube_objects[i].location[1] = 0
        cube_objects[i].location[2] = 0

        # Animate
        bpy.ops.object.select_all(action='DESELECT')
        path_objects[i].select = True
        bpy.data.scenes[SCENE_NAME].frame_current = FRAME_START
        bpy.data.curves['NurbsPath_' + str(i)].eval_time = 0
        bpy.data.curves['NurbsPath_' + str(i)].keyframe_insert(data_path =
            'eval_time')
        bpy.data.scenes[SCENE_NAME].frame_current = FRAME_END
        bpy.data.curves['NurbsPath_' + str(i)].eval_time = 100
        bpy.data.curves['NurbsPath_' + str(i)].keyframe_insert(data_path =
            'eval_time')

def track_cubes():
    """Print location and rotation of cubes along respective paths.

    Rotation in quaternions.

    """

    for i in range(cubes):
        data_files.append(open(dirname(dirname(os.path.realpath(__file__))) +
            os.sep + file_name + '_' + str(i) + '.csv', 'w'))

    for i in range(FRAME_END - FRAME_START + 1):
        current_frame = FRAME_START + i
        scene.frame_current = current_frame
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Refresh frame. Resolution must be low for window update to be fast.
        bpy.ops.render.render()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        for j in range(cubes):
            # World space coordinates
            translation_vector = cube_objects[j].matrix_world.to_translation()
            x = translation_vector[0]
            y = translation_vector[1]
            z = translation_vector[2]

            # Rotation
            rotation_vector = cube_objects[j].matrix_world.to_quaternion()
            w = rotation_vector[0]
            rx = rotation_vector[1]
            ry = rotation_vector[2]
            rz = rotation_vector[3]

            # Buffer to file
            output = "{0},{1},{2},{3},{4},{5},{6},{7}\n".format(current_frame,x,y,z,w,rx,ry,rz)
            data_files[j].write(output)
            blender_caller.plot_csv(data_files[j])

    # Close files
    for i in range(cubes):
        data_files[i].flush()
        data_files[i].close()

if __name__ == '__main__':
    main()
