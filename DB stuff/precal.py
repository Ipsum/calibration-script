'''
precal.py

Interface for precal station to database

By David Tyler
for Clark Solution


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
        else:
            self.OrderNumber.setBackgroundColor(QColor(128, self.green, 128))

    def slotSetCustomer(self,value):        
        customer = value
        patt = re.compile('[^A-Za-z ]*')
        if(patt.search(customer)):
            self.Customer.setBackgroundColor(QColor(self.red, 128, 128))
        else:
            self.Customer.setBackgroundColor(QColor(128, self.green, 128))

    def slotSetSN(self,value):   
        castingSn = raw_input('Casting Serial Number: ')
        patt = re.compile('[^0-9]*')
        if(patt.search(castingSn)):
            self.CastingSN.setBackgroundColor(QColor(self.red, 128, 128))
        else:
            self.CastingSN.setBackgroundColor(QColor(128, self.green, 128))

    def slotSetPCB(self,value):        
        pcbSn = raw_input('PCB Serial Number: ')
        patt = re.compile('[^0-9]*')
        if(patt.search(pcbSn)):
            self.pcbsn.setBackgroundColor(QColor(self.red, 128, 128))
        else:
            self.pcbsn.setBackgroundColor(QColor(128, self.green, 128))

    def slotSetSize(self,value):  
        sizeInd = raw_input('Size Index: ')
        patt = re.compile('[^0-7]*')
        if(patt.search(sizeInd)):
            self.SizeIndex.setBackgroundColor(QColor(self.red, 128, 128))
        else:
            self.SizeIndex.setBackgroundColor(QColor(128, self.green, 128))
  
    def slotSetFE(self,value):    
        fe = raw_input('First Echo(mV): ')
        patt = re.compile('[^0-9]*')
        if(patt.search(fe)):
            self.firstecho.setBackgroundColor(QColor(self.red, 128, 128))
        else:
            self.firstecho.setBackgroundColor(QColor(128, self.green, 128))

    def slotSetDz(self,value):    
        dz = raw_input('Dz: ')
        patt = re.compile('[^0-9.]*')
        if(patt.search(dz)):
            self.dz.setBackgroundColor(QColor(self.red, 128, 128))
        else:
            self.dz.setBackgroundColor(QColor(128, self.green, 128))

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
    
def save(db,so,customer,castingSn,pcbSn,sizeInd,fe,dz,):
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
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
    

def slotSetSO(self,value):
    so = raw_input('Sales Order Number: ')
    patt = re.compile('[^S0-9]*')
    while(patt.search(so)):
        so = raw_input('Invalid SO#, retry: ')

def slotSetCustomer(self,value):        
    customer = raw_input('Customer name: ')
    patt = re.compile('[^A-Za-z ]*')
    while(patt.search(customer)):
        customer = raw_input('Invalid customer name, retry: ')
   
def slotSetSN(self,value):   
    castingSn = raw_input('Casting Serial Number: ')
    patt = re.compile('[^0-9]*')
    while(patt.search(castingSn)):
        castingSn = raw_input('Invalid Casting SN, retry: ')

def slotSetPCB(self,value):        
    pcbSn = raw_input('PCB Serial Number: ')
    patt = re.compile('[^0-9]*')
    while(patt.search(pcbSn)):
        pcbSn = raw_input('Invalid PCB SN, retry: ')
  
def slotSetSize(self,value):  
    sizeInd = raw_input('Size Index: ')
    patt = re.compile('[^0-7]*')
    while(patt.search(sizeInd)):
        sizeInd = raw_input('Invalid Size Index, valid entry 0-7: ')
        
def slotSetFE(self,value):    
    fe = raw_input('First Echo(mV): ')
    patt = re.compile('[^0-9]*')
    while(patt.search(fe)):
        fe = raw_input('Invalid First Echo, retry: ')
    
def slotSetDz(self,value):    
    dz = raw_input('Dz: ')
    patt = re.compile('[^0-9.]*')
    while(patt.search(dz)):
        dz = raw_input('Invalid Dz, retry: ')
        
    correct = raw_input('Entry Correct? [y/n]: ')
    if (correct == 'y'):
            print save(dbpath,so,customer,castingSn,pcbSn,sizeInd,fe,dz,)
    else:
            print 'Discarded'
    
    again = raw_input('Another Meter? [y/n]: ')
