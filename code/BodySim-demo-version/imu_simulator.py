from imusim.all import *
import numpy as np
import os
import sys

dirname = os.path.dirname

SCALE = 0.01 # conversion scale from Blender

def simulate(filenames, fps):
	''' 
	Simulate each sensor and store the data to appropriate output filenames
	'''
	for f in filenames:
		#print ("simulating " + f + "...")
		#sys.stdout.flush()
		store_outputs(f, run_sim(read_inputs(f, fps), fps))


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



def run_sim(trajectory, fps):
	'''
	Run a simulation of an ideal IMU on trajectory data
	'''
	sim = Simulation()
	imu = IdealIMU(sim, trajectory)
	behaviour = BasicIMUBehaviour(imu, 1.0/fps)

	sim.time = trajectory.startTime
	sim.run(trajectory.endTime)
	sys.stdout.flush()

	imu_data = np.concatenate(([imu.accelerometer.rawMeasurements.timestamps], 
		imu.accelerometer.rawMeasurements.values, 
		imu.gyroscope.rawMeasurements.values))

	return imu_data


def store_outputs(filename, imu_data):
	'''
	Store output to appropriate filename
	'''

	# create output directory
	output_dir = dirname(dirname(filename)) + os.sep + 'sim'
	try:
		os.mkdir(output_dir)

	except:
		pass

	np.savetxt(output_dir + os.sep + filename.split(os.sep)[-1].split('.')[0] + '-i.csv', imu_data.transpose(), delimiter=',')


if __name__ == "__main__":
	simulate(sys.argv[1:], 30)
	#print('sucsess!')
	#sys.stdout.flush()