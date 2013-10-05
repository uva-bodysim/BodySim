'''
To use this file: look at blender caller.
'''

import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
import weakref
import math
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

    ax1 = plt.subplot(211)
    plt.title('Plot')

    for i in range(1, 4):
        ax1.plot(data[0], data[i], label=labels[i])

    plt.ylabel('location (cm)')
    plt.grid(True)
    plt.legend()

    ax2 = plt.subplot(212, sharex = ax1)

    for i in range(4, 8):
        ax2.plot(data[0], data[i], label=labels[i])

    plt.xlabel('time (s)')
    plt.ylabel('heading (rad)')
    plt.grid(True)
    plt.legend()
    ax2.autoscale(enable=False, axis='both')

    fig = plt.gcf()
    # Does not work on all systems...
    # multi = MultiCursor(fig.canvas, (ax1, ax2), color='r', lw=1, horizOn=False, vertOn=True)

    limits = ax1.axis()
    lcontainer = {'l1': None, 'l2': None}

    def onclick(event):
        if event.inaxes is not None:
            if lcontainer['l1'] != None:
                l = lcontainer['l1'].pop(0)
                wl = weakref.ref(l)
                l.remove()
                del l
                l = lcontainer['l2'].pop(0)
                wl = weakref.ref(l)
                l.remove()
                del l
            lcontainer['l1']= ax1.plot([event.xdata]*2, [limits[2], limits[3]], c="black")
            lcontainer['l2']= ax2.plot([event.xdata]*2, [-math.pi, math.pi], c="black")
            #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
            #        event.button, event.x, event.y, event.xdata, event.ydata)
            fig.canvas.draw()
            print event.xdata
            sys.stdout.flush()

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()


if __name__=="__main__":
    plot_file(sys.argv[1])
