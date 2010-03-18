'''
precal.py

Interface for precal station to database

By David Tyler
for Clark Solution
'''

import os, re, sqlite3
import ConfigParser

from PyQt4 import QtCore, QtGui
from datetime import date
from pcui import *

dbpath = "ClarkSonic.db"

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
    
print 'Precal Station Database entry'
os.system('title Precal Database Entry') #set commandprompt title

again = 'y'

while(again == 'y'):
    so = raw_input('Sales Order Number: ')
    patt = re.compile('[^S0-9]*')
    while(patt.search(so)):
        so = raw_input('Invalid SO#, retry: ')

    customer = raw_input('Customer name: ')
    patt = re.compile('[^A-Za-z ]*')
    while(patt.search(customer)):
        customer = raw_input('Invalid customer name, retry: ')
        
    castingSn = raw_input('Casting Serial Number: ')
    patt = re.compile('[^0-9]*')
    while(patt.search(castingSn)):
        castingSn = raw_input('Invalid Casting SN, retry: ')
        
    pcbSn = raw_input('PCB Serial Number: ')
    patt = re.compile('[^0-9]*')
    while(patt.search(pcbSn)):
        pcbSn = raw_input('Invalid PCB SN, retry: ')
        
    sizeInd = raw_input('Size Index: ')
    patt = re.compile('[^0-7]*')
    while(patt.search(sizeInd)):
        sizeInd = raw_input('Invalid Size Index, valid entry 0-7: ')
        
    fe = raw_input('First Echo(mV): ')
    patt = re.compile('[^0-9]*')
    while(patt.search(fe)):
        fe = raw_input('Invalid First Echo, retry: ')
        
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
