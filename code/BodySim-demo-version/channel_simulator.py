import numpy as np
import os
import sys
import math

dirname = os.path.dirname

SCALE = 0.01 # conversion scale from Blender

def simulate(filenames, fps):
	data = []
	for f in filenames:
		data.append(read_inputs(f, fps))

	# create output directory
	output_dir = dirname(dirname(filenames[0])) + os.sep + 'sim'
	try:
		os.mkdir(output_dir)

	except:
		pass

	channels = run_sim(data)
	for c in channels:
		#print(channels[c])
		np.savetxt(output_dir + os.sep + c + '-c.csv', channels[c].transpose(), delimiter=',')
	

def read_inputs(filename, fps):
	'''
	Produce trajectory from sensor position and orientation data
	'''
	f = open(filename, 'r').read().strip().split('\n')
	values = np.array([[float(a) for a in k.split(',')] for k in f]).transpose()

	# extract relevant data
	frames = values[0] # frames
	pos = values[1:4] * SCALE	# position values
	timestamps = (frames - 1)/fps

	return (filename.split(os.sep)[-1].split('.')[0], timestamps, pos)

def path_loss(d):
	return 20.0 *  math.log10(4.0 * math.pi * d / 125.0)

v_path_loss = np.vectorize(path_loss)

def run_sim(data):

	channels = {}

	for d in data:
		others = [v for v in data if v is not d]
		chan_data = np.zeros((len(others) + 1, len(others[0][1])))

		# timestamps
		chan_data[0] = d[1]
		
		for i in range(len(others)):
			mag = np.apply_along_axis(np.linalg.norm, 0, d[2] - others[i][2])
			#print(mag)
			chan_data[i+1] = v_path_loss(mag)
			#print(chan_data[i+1])

		channels[d[0]] = chan_data

	return channels

if __name__ == "__main__":
	simulate(sys.argv[1:], 30)
	print('sucsess!')
	sys.stdout.flush()


