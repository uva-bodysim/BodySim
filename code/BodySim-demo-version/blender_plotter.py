'''
To use this file: look at blender caller.
'''

import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
import weakref
import math
import sys
import os
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import wx
import wx.aui
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar

class Plot(wx.Panel):
    def __init__(self, parent, id = -1, dpi = None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2,2))
        self.canvas = Canvas(self, -1, self.figure)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND)
        sizer.Add(self.toolbar, 0 , wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)

class PlotNotebook(wx.Panel):
    def __init__(self, parent, id = -1):
        wx.Panel.__init__(self, parent, id=id)
        self.navtoolbar = parent.GetToolBar()
        self.nb = wx.aui.AuiNotebook(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.plots = []
        self.lines = []
        self.figures = {}
        self.limits = []

    def add(self,name="plot"):
       page = Plot(self.nb)
       self.nb.AddPage(page,name)
       self.figures[page.figure] = page.toolbar
       return page.figure

    def plot_file(self, filename, fig, plot_type, fps):

        labels = {'-raw': ['t','x','y','z','quat_w','quat_x','quat_y','quat_z'],
                    '-imu': ['t','x','y','z','x','y','z'],
                    '-chan': ['t','pathloss', 'pathloss']}
        lengths = {'-raw': 8, '-imu': 7}

        ranges = {'-raw': [range(1,4), range(4,8)], '-imu': [range(1,4), range(4,7)], 
                    '-chan': [range(1,2), range(2,3)]}
        ylabels = {'-raw': ['location (cm)', 'heading (rad)'], 
                    '-imu': ['acceleration (m/s^2)', 'angular velocity (deg/s)'],
                    '-chan': ['pathloss (dB)', 'pathloss(dB)']}
        xlabel = {'-raw': 'frame no.', '-imu': 'time (s)', '-chan': 'time (s)'}

        data = []
        try:
            f = open(filename, 'r').read().strip().split('\n')
            values = [[float(a) for a in k.split(',')] for k in f]
            data = zip(*values)
            if(plot_type != '-chan'):
                if len(data) != lengths[plot_type]:
                    print("Bad file format! Make sure each line has {0} values!".format(lengths[plot_type]))
        except IOError:
            print("Bad file name!")
            return
        except:
            print("Bad file format! Make sure each line has {0} values!".format(lengths[plot_type]))
            return

        share = None
        if len(self.plots) != 0:
            share = self.plots[0][0]

        # 211: Two rows, one column, first subplot. Numbering starts row first.
        ax1 = self.addSubfig(fig, 211, xlabel[plot_type], labels[plot_type][1:4], ylabels[plot_type][0], data[0], data[1:4], share)

        ax2 = self.addSubfig(fig, 212, xlabel[plot_type], labels[plot_type][4:8], ylabels[plot_type][1], data[0], data[4:8], ax1)

        # Makes sure the limits of the vertical line spans the y axis
        lim = ax1.axis()
        if self.limits == []: 
            self.limits = [lim[2], lim[3]]
        if lim[2] < self.limits[0]: 
            self.limits[0] = lim[2]
        if lim[3] > self.limits[1]: 
            self.limits[1] = lim[3]

        self.plots.append((ax1, ax2),)
        self.bind_to_onclick_event(fig, plot_type)

    def addSubfig(self,fig, layout, xlabel, labels, ylabel, xData, yDatum, shareAxis):
        ax1 = fig.add_subplot(layout, sharex=shareAxis)
        ax1.set_title('Plot')
        for i in range(len(yDatum)):
            ax1.plot(xData, yDatum[i], label=labels[i])
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        ax1.grid(True)
        ax1.legend()
        ax1.autoscale(enable=False, axis='both')
        return ax1

    def bind_to_onclick_event(self, fig, plot_type):
        def onclick(event):
            # If click in axis and toolbar mode is nothing
            if event.inaxes is not None and self.figures[fig].mode == "":
                #removes all existing lines
                for line in self.lines:
                    l = line.pop(0)
                    wl = weakref.ref(l)
                    l.remove()
                    del l
                self.lines = []
                #adds new markers on where we are
                for plot in self.plots:
                    self.lines.append(plot[0].plot([event.xdata]*2, [self.limits[0], self.limits[1]], c="black"))

                    if(plot_type == '-raw'):
                        self.lines.append(plot[1].plot([event.xdata]*2, [-math.pi, math.pi], c="black"))
                    else:
                        self.lines.append(plot[1].plot([event.xdata]*2, [self.limits[0], self.limits[1]], c="black"))

                for figure in self.figures:
                    fig.canvas.draw()
                if (plot_type == '-raw'):
                    print event.xdata
                    sys.stdout.flush()

                if (plot_type in {'-imu', '-chan'}):
                    print (event.xdata * fps) + 1
                    sys.stdout.flush()

        cid = fig.canvas.mpl_connect('button_press_event', onclick)

class PlotFrame(wx.Frame):
    """Subclass of wx.Frame that adds an onclose event handler."""

    def __init__(self):
        super(PlotFrame, self).__init__(None, -1, 'Plotter')
        self.Bind(wx.EVT_CLOSE, self.onclose)

    def onclose(self, event):
        """Prints "quit" to the pipe to let the blender operator know to stop running."""
        print("quit")
        sys.stdout.flush()
        self.Destroy()
   
def plot_file(plot_type, fps, filenames):
    app = wx.PySimpleApp()
    frame = PlotFrame() 
    plotter = PlotNotebook(frame)
    for filename in filenames:
        fig = plotter.add(os.path.splitext(os.path.basename(filename))[0])
        plotter.plot_file(filename, fig, plot_type, fps,)
    frame.Show()
    app.MainLoop()

if __name__=="__main__":
    plot_file(sys.argv[1], float(sys.argv[2]), sys.argv[3:])
