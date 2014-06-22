import sys, os, ast
import matplotlib
import weakref
matplotlib.use('Qt4Agg')
import pylab

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

from PySide import QtCore, QtGui

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(0,0, 650,650)
        self.tab_widget = QtGui.QTabWidget()
        self.resize(650,650)
        self.setMinimumSize(650,650)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.tab_widget)
        self.setLayout(vbox)
        self.setWindowTitle("BodySim")
        self.toolbars = {}
        self.lines = []
        self.plots = []

    def add_tab(self, name="plot"):
        qscroll = QtGui.QScrollArea(self)
        self.tab_widget.addTab(qscroll, name)
        qscroll.setGeometry(QtCore.QRect(0, 0, 500, 500))
        qscroll.setFrameStyle(QtGui.QFrame.NoFrame)
        qscrollContents = QtGui.QWidget()
        qscrollLayout = QtGui.QVBoxLayout(qscrollContents)
        qscrollLayout.setGeometry(QtCore.QRect(0, 0, 1000, 1000))
        qscroll.setWidget(qscrollContents)
        qscroll.setWidgetResizable(True)
        qscrollContents.setLayout(qscrollLayout)
        return (qscrollLayout, qscrollContents)

    def closeEvent(self, event):
        print 'quit'
        sys.stdout.flush()

    def bind_to_onclick_event(self, fig):
        def onclick(event):
            # If click in axis and toolbar mode is nothing
            if event.inaxes is not None and self.toolbars[fig].mode == "":
                #removes all existing lines
                for line in self.lines:
                    l = line.pop(0)
                    wl = weakref.ref(l)
                    l.remove()
                    del l
                self.lines = []

                for plot in self.plots:
                    if event.inaxes.get_xlim()[1] == plot.get_xlim()[1]:
                        self.lines.append(plot.plot([event.xdata]*2, [plot.get_ylim()[0], plot.get_ylim()[1]], c="black"))
                    else:
                        self.lines.append(plot.plot([event.xdata / float(event.inaxes.get_xlim()[1]) * plot.get_xlim()[1]]*2,
                                          [plot.get_ylim()[0], plot.get_ylim()[1]], c="black"))

                for figure in self.toolbars:
                    figure.canvas.draw()

                print (event.xdata / float(event.inaxes.get_xlim()[1])) * 100
                sys.stdout.flush()


        cid = fig.canvas.mpl_connect('button_press_event', onclick)

def plot_file(fps, base_dir, string_graph_map):
    app = QtGui.QApplication('Bodysim')
    frame = MainWindow()

    graph_map = ast.literal_eval(string_graph_map)

    for sensor in graph_map:
        layout_contents = frame.add_tab(sensor)
        for plugin in graph_map[sensor]:
            data = get_data(base_dir + os.sep + plugin + os.sep +'sensor_' + sensor + '.csv')
            for variable_group in graph_map[sensor][plugin]:
                qfigWidget = QtGui.QWidget(layout_contents[1])
                fig = Figure((5.0, 4.0), dpi=100)
                canvas = FigureCanvas(fig)
                canvas.setParent(qfigWidget)
                toolbar = NavigationToolbar(canvas, qfigWidget)
                axes = fig.add_subplot(111)
                axes.set_title(plugin + ' ' + variable_group[2])
                yDatum = [data[variable[1]] for variable in graph_map[sensor][plugin][variable_group]]
                yLabels = [variable[0] for variable in graph_map[sensor][plugin][variable_group]]
                for i in range(len(yDatum)):
                    axes.plot(data[0], yDatum[i], label=yLabels[i])
                axes.grid(True)
                axes.legend()
                axes.autoscale(enable=False, axis='both')
                axes.set_xlabel(variable_group[0])
                axes.set_ylabel(variable_group[1])

                # place plot components in a layout
                plotLayout = QtGui.QVBoxLayout()
                plotLayout.addWidget(canvas)
                plotLayout.addWidget(toolbar)
                qfigWidget.setLayout(plotLayout)
                frame.toolbars[fig] = toolbar
                frame.plots.append(axes)

                canvas.setMinimumSize(canvas.size())
                frame.bind_to_onclick_event(fig)
                layout_contents[0].addWidget(qfigWidget)

    frame.show()
    sys.exit(app.exec_())

def get_data(filename):

    data = []
    try:
        f = open(filename, 'r').read().strip().split('\n')
        values = [[float(a) for a in k.split(',')] for k in f]
        data = zip(*values)
    except:
        print("Bad file format! Each row must have the same number of values.")
        return

    return data

if __name__ == "__main__":
    plot_file(float(sys.argv[1]), sys.argv[2], sys.argv[3])
