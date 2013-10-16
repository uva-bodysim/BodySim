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

    def plot_file(self, filename, fig):

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

        share = None
        if len(self.plots) != 0:
            share = self.plots[0][0]

        ax1 = fig.add_subplot(211, sharex=share)
        ax1.set_title('Plot')
        for i in range(1, 4):
            ax1.plot(data[0], data[i], label=labels[i])
        ax1.set_ylabel('location (cm)')
        ax1.grid(True)
        ax1.legend()
        ax1.autoscale(enable=False, axis='both')

        ax2 = fig.add_subplot(212, sharex = ax1)
        for i in range(4, 8):
            ax2.plot(data[0], data[i], label=labels[i])
        ax2.set_xlabel('time (s)')
        ax2.set_ylabel('heading (rad)')
        ax2.grid(True)
        ax2.legend()
        ax2.autoscale(enable=False, axis='both')

        self.plots.append((ax1, ax2))
        # Makes sure the limits of the vertical line spans the y axis
        lim = ax1.axis()
        if self.limits == []: 
            self.limits = [lim[2], lim[3]]
        if lim[2] < self.limits[0]: 
            self.limits[0] = lim[2]
        if lim[3] > self.limits[1]: 
            self.limits[1] = lim[3]

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
                    self.lines.append(plot[1].plot([event.xdata]*2, [-math.pi, math.pi], c="black"))
                #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
                #        event.button, event.x, event.y, event.xdata, event.ydata)
                for figure in self.figures:
                    fig.canvas.draw()
                print event.xdata
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
   
def plot_file(filenames):
    app = wx.PySimpleApp()
    frame = PlotFrame() 
    plotter = PlotNotebook(frame)
    for filename in filenames:
        fig = plotter.add(os.path.splitext(os.path.basename(filename))[0])
        plotter.plot_file(filename, fig)
    frame.Show()
    app.MainLoop()

if __name__=="__main__":
    plot_file(sys.argv[1:])
