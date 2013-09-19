'''
To use this file: look at blender caller.
'''

import pylab
import sys

def plot_file(filename):
    labels = ['t','x','y','z','quat_w','quat_x','quat_y','quat_z']
    data = []
    try:
        f = open(filename, 'r').read().strip().split('\n')
        values = [[float(a) for a in k.split(',')] for k in f]
        data = zip(*values)
        if len(data) != 8:
            print("Bad file format! Make sure each line has 8 values!")
    except IOError:
        print("Bad file name!")
        return
    except:
        print("Bad file format! Make sure each line has 8 values!")
        return
    
    for i in range(1, 8):
        pylab.plot(data[0], data[i], label=labels[i])

    pylab.xlabel('time (s)')
    pylab.ylabel('location (?)')
    pylab.title('Coordinates')
    pylab.grid(True)
    pylab.legend()
    pylab.show()

if __name__=="__main__":
    plot_file(sys.argv[1])
