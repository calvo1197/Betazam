from matplotlib import pyplot
#Clase que permite ver los datos obtenidos del espectro
class VisualiserPlot():
  def __init__(self):
    pass

  @staticmethod
  def show(data):
    pyplot.plot(data)
    pyplot.show()
