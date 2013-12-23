"""
IMPORTANT!
Script that creates the Sim Tools panel. Note that the operators that it uses
must be registered first before this panel can be registered. These files are:
    graph_operator.py (for plotting, both IMU and motion)
    IMUGenerateOperator.py (for IMU data generation)
    TrackSensorOperator.py (for motion data generation)
"""
import bpy

class SimTools(bpy.types.Panel):
    bl_label = "Sim Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("bodysim.track_sensors", text = "Run Motion Simulation")
        self.layout.operator("bodysim.generate_imu", text = "Run IMU Simulation")
        self.layout.operator("bodysim.plot_motion", text = "Plot Motion Data").plot_type = "-raw"
        self.layout.operator("bodysim.plot_motion", text = "Plot IMU Data").plot_type = "-imu"
        
bpy.utils.register_module(__name__)
