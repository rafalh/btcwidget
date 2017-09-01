from matplotlib.figure import Figure
import matplotlib.cm as cm
import matplotlib.ticker as ticker
# Possibly this rendering backend is broken currently
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas


class MultipleLocatorWithMargin(ticker.MultipleLocator):

    def __init__(self, base=600, left_margin=0.0, right_margin=0.0):
        ticker.MultipleLocator.__init__(self, base)
        self._left_margin = left_margin
        self._right_margin = right_margin

    def view_limits(self, dmin, dmax):
        dmin, dmax = ticker.MultipleLocator.view_limits(self, dmin, dmax)
        size = dmax - dmin
        dmin -= size * self._left_margin
        dmax += size * self._right_margin
        return dmin, dmax

class Graph(FigureCanvas):
    def __init__(self, dark):
        self.figure = Figure(figsize=(0, 1000), dpi=75, facecolor='w', edgecolor='k')
        self.axes = self.figure.add_axes([0.12, 0.08, 0.75, 0.90])
        self.figure.patch.set_alpha(0)
        self.axes.margins(0, 0.05)
        self.axes.ticklabel_format(useOffset=False)
        self.axes.xaxis.set_major_locator(MultipleLocatorWithMargin(600, 0, 0.03))
        self.axes.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: "{}m".format(int(x/60))))
        if dark:
            self.axes.patch.set_facecolor('black')
        FigureCanvas.__init__(self, self.figure)
        self.set_size_request(400, 300)
        self.lines = {}
        self.texts = {}

    def set_data(self, index, x, y, color):
        if len(y) == 0:
            return
        if not index in self.lines:
            line, = self.axes.plot(x, y, color=color)
            self.lines[index] = line
        else:
            line = self.lines[index]
            line.set_data(x, y)

        self.axes.relim()

        price_text = '{:.2f}'.format(y[-1])
        xmin, xmax = self.axes.get_xbound()
        xsize = xmax - xmin
        text_x, text_y = xmax+xsize*0.01, y[-1]

        if not index in self.texts:
            text = self.axes.text(text_x, text_y, price_text, color='w', size='x-small')
            text.set_bbox(dict(facecolor=line.get_color(), edgecolor='none', alpha=0.5))
            text.set_ha('left')
            self.texts[index] = text
        else:
            text = self.texts[index]
            text.set_y(text_y)
            text.set_text(price_text)

        for i in self.texts:
            self.texts[i].set_x(text_x)

        self.axes.autoscale_view(False)
        self.draw()

    def set_dark(self, dark):
        if dark:
            self.axes.patch.set_facecolor('black')
        else:
            self.axes.patch.set_facecolor('white')

    def clear(self):
        for i in self.lines:
            self.axes.lines.remove(self.lines[i])
        for i in self.texts:
            self.axes.texts.remove(self.texts[i])
        self.lines = {}
        self.texts = {}
        self.draw()
