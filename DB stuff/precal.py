'''
precal.py

Interface for precal station to database

By David Tyler
for Clark Solutions


references:
http://www.commandprompt.com/community/pyqt/x1408
http://www.riverbankcomputing.com/static/Docs/PyQt4/html/qlineedit.html#returnPressed
http://wiki.python.org/moin/JonathanGardnerPyQtTutorial
http://diotavelli.net/PyQtWiki/Creating_GUI_Applications_with_PyQt_and_Qt_Designer
'''

import os, re, sqlite3
import ConfigParser

from PyQt4 import QtCore, QtGui
from datetime import date
from pcui import *

dbpath = "ClarkSonic.db"

class MainWindow(Ui_MainWindow):
    def __init__(self, parent=None, name=None, fl=0):
        Ui_MainWindow.__init__(self,parent,name,fl)
        
        self.connect(self.buttonBox, SIGNAL("accepted()"), self.save)
        self.connect(self.dz, SIGNAL("editingFinished()"), self.slotSetDz)
		self.connect(self.firstecho, SIGNAL("editingFinished()"), self.slotSetFE)
		self.connect(self.SizeIndex, SIGNAL("editingFinished()"), self.slotSetSize)
		self.connect(self.Customer, SIGNAL("editingFinished()"), self.slotSetCustomer)
		self.connect(self.OrderNumber, SIGNAL("editingFinished()"), self.slotSetSO)
		self.connect(self.CastingSN, SIGNAL("editingFinished()"), self.slotSetSN)
		
	def slotSetSO(self,value):
        so = value
        patt = re.compile('[^S0-9]*')
        if(patt.search(so)):
            self.OrderNumber.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "You must specify a Sales Order Number",
                QMessageBox.Ok)
        else:
            self.OrderNumber.setBackgroundColor(QColor(128, self.green, 128))
            self.so = value
            
    def slotSetCustomer(self,value):        
        customer = value
        patt = re.compile('[^A-Za-z ]*')
        if(patt.search(customer)):
            self.Customer.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "You must specify a Sales Order Number",
                QMessageBox.Ok)
        else:
            self.Customer.setBackgroundColor(QColor(128, self.green, 128))
            self.cust = value
            
    def slotSetSN(self,value):   
        castingSn = raw_input('Casting Serial Number: ')
        patt = re.compile('[^0-9]*')
        if(patt.search(castingSn)):
            self.CastingSN.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "You must specify a Sales Order Number",
                QMessageBox.Ok)
        else:
            self.CastingSN.setBackgroundColor(QColor(128, self.green, 128))
            self.csn = value
            
    def slotSetPCB(self,value):        
        pcbSn = raw_input('PCB Serial Number: ')
        patt = re.compile('[^0-9]*')
        if(patt.search(pcbSn)):
            self.pcbsn.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "You must specify a Sales Order Number",
                QMessageBox.Ok)
        else:
            self.pcbsn.setBackgroundColor(QColor(128, self.green, 128))
            self.psn = value
            
    def slotSetSize(self,value):  
        sizeInd = raw_input('Size Index: ')
        patt = re.compile('[^0-8]*')
        if(patt.search(sizeInd)):
            self.SizeIndex.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "Size Indexs: 3/4\"=0, 1\"=1, 1.5\"=2, 2\"=3, 3\"=4, 4\"=5, 6\"=6, 8\"=7 10\"=8",
                QMessageBox.Ok)
        else:
            self.SizeIndex.setBackgroundColor(QColor(128, self.green, 128))
            self.si = value
            
    def slotSetFE(self,value):    
        fe = raw_input('First Echo(mV): ')
        patt = re.compile('[^0-9]*')
        if(patt.search(fe)):
            self.firstecho.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "You must specify a valid First Echo",
                QMessageBox.Ok)
        else:
            self.firstecho.setBackgroundColor(QColor(128, self.green, 128))
            self.fe = value
            
    def slotSetDz(self,value):    
        dz = raw_input('Dz: ')
        patt = re.compile('[^0-9.]*')
        if(patt.search(dz)):
            self.dz.setBackgroundColor(QColor(self.red, 128, 128))
            QMessageBox.critical(self,
                "Invalid Entry", "You must specify a valid Dz",
                QMessageBox.Ok)
        else:
            self.dz.setBackgroundColor(QColor(128, self.green, 128))
            self.dzval = value
    
    def save(self):
        try:
            dbsave(db,self.so,self.cust,self.csn,self.psn,self.si,self.fe,self.dzval) 
        except sqlite3.Error:
            QMessageBox.critical(self,
                "Database Error", "There was an error saving your data",
                QMessageBox.Ok)
                
def dbconnect(db):
    "check to see that our db has the clarksonic table and return a connection."
    conn = sqlite3.connect(db)

    conn.execute("CREATE TABLE IF NOT EXISTS clarksonic(id integer primary key "
                 "autoincrement, customer text, salesorder text, "
                 "pcb integer, casting integer, date datetime, "
                 "calibrator text, k real, dz real, pol text, "
                 "dir integer, pulse integer, liters integer, fe integer, size integer);")

    conn.commit()

    return conn
    
def dbsave(db,so,customer,castingSn,pcbSn,sizeInd,fe,dz,):
    conn = dbconnect(db)
    cursor = conn.cursor()
    
    command = "insert into clarksonic(customer,salesorder,pcb,casting,dz,fe,size) values(?,?,?,?,?,?,?)"
    cursor.execute(command, (customer,so,pcbSn,castingSn,dz,fe,sizeInd))

    conn.commit()
    conn.close()
    
    return "Sucess"
    
if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()",a,SLOT("quit()"))
    w = MainWindow()
    QObject.connect(buttonBox, SIGNAL("accepted()"), SLOT("close()")
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
    


        
    correct = raw_input('Entry Correct? [y/n]: ')
    if (correct == 'y'):
            print save(dbpath,so,customer,castingSn,pcbSn,sizeInd,fe,dz,)
    else:
            print 'Discarded'
    
    again = raw_input('Another Meter? [y/n]: ')
