from imusim.all import *
import numpy as np
import os
import sys


SCALE = 0.01 # conversion scale from Blender

PARAMS = {'x_acc': 0,
			'y_acc': 1,
			'z_acc': 2,
			'x_gyro': 0,
			'y_gyro': 1,
			'z_gyro': 2}

dirname = os.path.dirname

def simulate(filename, fps, params):
	'''
	Simulate each sensor and store the data to appropriate output filenames
	'''
	store_outputs(filename, run_sim(read_inputs(filename, fps), fps, params))


def read_inputs(filename, fps):
	'''
	Produce trajectory from sensor position and orientation data
	'''
	f = open(filename, 'r').read().strip().split('\n')
	values = np.array([[float(a) for a in k.split(',')] for k in f]).transpose()

	# extract relevant data
	frames = values[0] # frames
	pos = values[1:4] * SCALE	# position values
	quat = values[4:9]	# quaternion values

	timestamps = (frames - 1)/fps

	position_ts = TimeSeries(timestamps, pos)
	rotation_ts = TimeSeries(timestamps, QuaternionArray(quat.transpose()))

	# create Splined Trajectory
	trajectory = SplinedTrajectory(SampledTrajectory(position_ts, rotation_ts))

	return trajectory



def run_sim(trajectory, fps, params):
	'''
	Run a simulation of an ideal IMU on trajectory data
	'''
	sim = Simulation()
	imu = IdealIMU(sim, trajectory)
	behaviour = BasicIMUBehaviour(imu, 1.0/fps)

	sim.time = trajectory.startTime
	sim.run(trajectory.endTime)
	sys.stdout.flush()

	imu_data = imu.accelerometer.rawMeasurements.timestamps

	for p in params:
		if p.split('_')[1] == 'acc':
			imu_data = np.vstack((imu_data, imu.accelerometer.rawMeasurements.values[PARAMS[p]]))
		else:
			imu_data = np.vstack((imu_data, imu.gyroscope.rawMeasurements.values[PARAMS[p]]))

	return imu_data


def store_outputs(filename, imu_data):
	'''
	Store output to appropriate filename
	'''

	# create output directory
	output_dir = dirname(dirname(filename)) + os.sep + 'IMU'
	try:
		os.mkdir(output_dir)

	except:
		pass

	np.savetxt(output_dir + os.sep + filename.split(os.sep)[-1].split('.')[0] + '.csv', imu_data.transpose(), delimiter=',')

'''
Main function: assume input is <path-to-sensor-data> <frames-per-second> <parameters>
'''
if __name__ == "__main__":
	sensor_file_path = sys.argv[1]
	fps = int(sys.argv[2])
	params = [str(param) for param in sys.argv[3:]] 
	simulate(sensor_file_path, fps, params)
	#print('sucsess!')
	#sys.stdout.flush()