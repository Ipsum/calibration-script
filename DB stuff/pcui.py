# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pcui.ui'
#
# Created: Thu Mar 18 15:51:13 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(485, 227)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.dz = QtGui.QLineEdit(self.centralwidget)
        self.dz.setGeometry(QtCore.QRect(200, 110, 113, 20))
        self.dz.setObjectName("dz")
        self.firstecho = QtGui.QLineEdit(self.centralwidget)
        self.firstecho.setGeometry(QtCore.QRect(300, 70, 113, 20))
        self.firstecho.setObjectName("firstecho")
        self.SizeIndex = QtGui.QLineEdit(self.centralwidget)
        self.SizeIndex.setGeometry(QtCore.QRect(90, 70, 113, 20))
        self.SizeIndex.setObjectName("SizeIndex")
        self.Customer = QtGui.QLineEdit(self.centralwidget)
        self.Customer.setGeometry(QtCore.QRect(300, 10, 113, 20))
        self.Customer.setObjectName("Customer")
        self.OrderNumber = QtGui.QLineEdit(self.centralwidget)
        self.OrderNumber.setGeometry(QtCore.QRect(90, 10, 113, 20))
        self.OrderNumber.setObjectName("OrderNumber")
        self.CastingSN = QtGui.QLineEdit(self.centralwidget)
        self.CastingSN.setGeometry(QtCore.QRect(90, 40, 113, 20))
        self.CastingSN.setObjectName("CastingSN")
        self.buttonBox = QtGui.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(180, 160, 156, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 71, 21))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 61, 21))
        self.label_2.setObjectName("label_2")
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(170, 110, 21, 21))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(240, 10, 51, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 70, 51, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(240, 70, 51, 16))
        self.label_7.setObjectName("label_7")
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(240, 40, 51, 21))
        self.label_3.setObjectName("label_3")
        self.pcbsn = QtGui.QLineEdit(self.centralwidget)
        self.pcbsn.setGeometry(QtCore.QRect(300, 40, 113, 20))
        self.pcbsn.setObjectName("pcbsn")
        self.fault = QtGui.QRadioButton(self.centralwidget)
        self.fault.setGeometry(QtCore.QRect(10, 110, 82, 21))
        self.fault.setChecked(True)
        self.fault.setObjectName("fault")
        self.buttonGroup = QtGui.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.fault)
        self.direction = QtGui.QRadioButton(self.centralwidget)
        self.direction.setGeometry(QtCore.QRect(10, 130, 82, 17))
        self.direction.setChecked(False)
        self.direction.setObjectName("direction")
        self.buttonGroup.addButton(self.direction)
        self.pulse = QtGui.QRadioButton(self.centralwidget)
        self.pulse.setGeometry(QtCore.QRect(10, 150, 82, 17))
        self.pulse.setObjectName("pulse")
        self.buttonGroup.addButton(self.pulse)
        self.liters = QtGui.QCheckBox(self.centralwidget)
        self.liters.setGeometry(QtCore.QRect(100, 130, 70, 17))
        self.liters.setObjectName("liters")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 485, 20))
        self.menubar.setObjectName("menubar")
        self.menuPrecal_Station = QtGui.QMenu(self.menubar)
        self.menuPrecal_Station.setObjectName("menuPrecal_Station")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionPreCal_Data_Entry = QtGui.QAction(MainWindow)
        self.actionPreCal_Data_Entry.setObjectName("actionPreCal_Data_Entry")
        self.actionClear_Form = QtGui.QAction(MainWindow)
        self.actionClear_Form.setObjectName("actionClear_Form")
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuPrecal_Station.addAction(self.actionClear_Form)
        self.menuPrecal_Station.addSeparator()
        self.menuPrecal_Station.addAction(self.actionExit)
        self.menubar.addAction(self.menuPrecal_Station.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), QtCore.SLOT("close()")
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        

            
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Order Number", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Casting SN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MainWindow", "DZ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Customer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Size Index", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "First Echo", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "PCB SN", None, QtGui.QApplication.UnicodeUTF8))
        self.fault.setText(QtGui.QApplication.translate("MainWindow", "Fault", None, QtGui.QApplication.UnicodeUTF8))
        self.direction.setText(QtGui.QApplication.translate("MainWindow", "Direction", None, QtGui.QApplication.UnicodeUTF8))
        self.pulse.setText(QtGui.QApplication.translate("MainWindow", "Pulse", None, QtGui.QApplication.UnicodeUTF8))
        self.liters.setText(QtGui.QApplication.translate("MainWindow", "Liters", None, QtGui.QApplication.UnicodeUTF8))
        self.menuPrecal_Station.setTitle(QtGui.QApplication.translate("MainWindow", "Precal Station", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreCal_Data_Entry.setText(QtGui.QApplication.translate("MainWindow", "PreCal Data Entry", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClear_Form.setText(QtGui.QApplication.translate("MainWindow", "Clear Form", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))

