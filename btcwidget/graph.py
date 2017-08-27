from matplotlib.figure import Figure
import matplotlib.cm as cm
import matplotlib.ticker as ticker
# Possibly this rendering backend is broken currently
# from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas


class Graph(FigureCanvas):
    def __init__(self, dark):
        self.figure = Figure(figsize=(0, 1000), dpi=75, facecolor='w', edgecolor='k')
        self.axes = self.figure.add_axes([0.11, 0.1, 0.78, 0.9])
        self.figure.patch.set_alpha(0)
        self.axes.margins(0, 0.05)
        self.axes.ticklabel_format(useOffset=False)
        self.axes.xaxis.set_major_locator(ticker.MultipleLocator(600))
        self.axes.xaxis.set_major_formatter(ticker.FormatStrFormatter('%ds'))
        if dark:
            self.axes.patch.set_facecolor('black')
        FigureCanvas.__init__(self, self.figure)
        self.set_size_request(400, 300)
        self.lines = {}
        self.texts = {}

    def set_data(self, index, x, y, color):
        if len(y) == 0:
            return
        price_text = '{:.2f}'.format(y[-1])
        if not index in self.lines:
            line, = self.axes.plot(x, y, color=color)
            text = self.axes.text(x[-1], y[-1], price_text, color='w', size='x-small')
            text.set_bbox(dict(facecolor=line.get_color(), edgecolor='none', alpha=0.5))
            text.set_ha('left')
            self.lines[index] = line
            self.texts[index] = text
        else:
            line, text = self.lines[index], self.texts[index]
            line.set_data(x, y)
            self.axes.relim()
            self.axes.autoscale_view()
            text.set_position((x[-1], y[-1]))
            text.set_text(price_text)
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
