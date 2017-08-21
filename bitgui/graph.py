from matplotlib.figure import Figure
import matplotlib.cm as cm
#Possibly this rendering backend is broken currently
#from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas


class Graph(FigureCanvas):
	def __init__(self):
		self.figure = Figure(figsize=(100, 100), dpi=75)
		self.axes = self.figure.add_subplot(111)
		self.axes.ticklabel_format(useOffset=False)
		self.axes.margins(0.1, 0.1)
		self.axes.patch.set_facecolor('black')
		FigureCanvas.__init__(self, self.figure)
		self.set_size_request(400,400)
		self.lines = {}
		#self.set_data(1, [1,2,3,4,5,6,7], [1000, 1002, 1004, 1003, 900, 950, 1000])
		#self.set_data(2, [1,2,3,4,5,6,7], [900, 1000, 1000, 1000, 1000, 1000, 1000])

	def set_data(self, index, x, y):
		#print(x, y)
		#x = range(1,len(y)+1)
		if not index in self.lines:
			line, = self.axes.plot(x, y)
			self.lines[index] = line
		else:
			line = self.lines[index]
			line.set_data(x, y)
		self.draw()
