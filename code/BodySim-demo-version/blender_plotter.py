'''
To use this file: look at blender caller.
'''

import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
import weakref
import math
import sys
import os
import ast
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

    def plot_file(self, fig, subfiglist):
        # Makes sure the limits of the vertical line spans the y axis
        lim = subfiglist[0].axis()
        if self.limits == []: 
            self.limits = [lim[2], lim[3]]
        if lim[2] < self.limits[0]: 
            self.limits[0] = lim[2]
        if lim[3] > self.limits[1]: 
            self.limits[1] = lim[3]

        self.plots.append(subfiglist,)
        #self.bind_to_onclick_event(fig, plot_type)

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

    def bind_to_onclick_event(self, fig):
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
                    #print dir(event.inaxes)
                    print event.inaxes.get_xlim()
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

class Subfig:

    def __init__(self, parent_fig, max_cols, row_number, xunit, yunit, xlabels, ylabels, xdata, ydata):
        self.total_rows = None
        self.parent_fig = parent_fig
        self.max_cols = max_cols
        self.row_number = row_number
        self.xunit = xunit
        self.yunit = yunit
        self.xlabels = xlabels
        self.ylabels = ylabels
        self.xdata = xdata
        self.ydata = ydata
   
def plot_file(fps, base_dir, string_graph_map):
    app = wx.PySimpleApp()
    frame = PlotFrame()
    plotter = PlotNotebook(frame)

    graph_map = ast.literal_eval(string_graph_map)
    fig_map = {}

    for sensor in graph_map:
        fig = plotter.add(sensor)
        fig_map[sensor] = {}
        fig_map[sensor]['total_rows'] = 0
        fig_map[sensor]['subfig'] = []
        for plugin in graph_map[sensor]:
            data = get_data(base_dir + os.sep + plugin + os.sep +'sensor_' + sensor + '.csv')
            for variable_group in graph_map[sensor][plugin]:
                fig_map[sensor]['subfig'].append(Subfig(fig, 1, fig_map[sensor]['total_rows'] + 1, variable_group[0], variable_group[1], 't',
                 [variable[0] for variable in graph_map[sensor][plugin][variable_group]],
                 data[0],
                 [data[variable[1]] for variable in graph_map[sensor][plugin][variable_group]]))
                fig_map[sensor]['total_rows'] += 1

    for fig in fig_map:
        ax_list = []
        for sub_fig in fig_map[fig]['subfig']:
            ax_list.append(plotter.addSubfig(sub_fig.parent_fig, str(fig_map[fig]['total_rows']) + str(sub_fig.max_cols) + str(sub_fig.row_number),
            sub_fig.xunit, sub_fig.ylabels, sub_fig.yunit, sub_fig.xdata, sub_fig.ydata, None))

        plotter.plot_file(fig, tuple(ax_list))


    frame.Show()
    app.MainLoop()

def get_data(filename):
    with open('test.txt', 'w') as f:
        f.write(filename)

    data = []
    try:
        f = open(filename, 'r').read().strip().split('\n')
        values = [[float(a) for a in k.split(',')] for k in f]
        data = zip(*values)
    except:
        print("Bad file format! Each row must have the same number of values.")
        return

    return data

if __name__=="__main__":
    plot_file(float(sys.argv[1]), sys.argv[2], sys.argv[3])