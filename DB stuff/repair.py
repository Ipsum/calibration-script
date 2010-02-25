from PyQt4 import *
from lookup import *
import os,sys

 # Create a class for our main window
class Main(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		# This is always the same
		self.ui=Ui_Dialog()
		self.ui.setupUi(self)

def main():
	# Again, this is boilerplate, it's going to be the same on
	# almost every app you write
	app = QtGui.QApplication(sys.argv)
	window=Main()
	window.show()
	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
