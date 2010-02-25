'''
clarksonicDB.py

Interface for interacting directly with the ClarkSonic database containing:
Calibration data (K, Dz, Polarity, Pre-trig, Dir/Flt, Pulse, G/L, FE)
Customer Name
Sales Order #
Date
Board/PCB SN
Calibrator name

Using SQLite3 for database backend

By: David Tyler for Clark Solutions
'''

import os
import re
import sqlite3

from datetime import date

                 "k real, dz real, pol text, ptrig real, "
                 "dir integer, pulse integer, liters integer, fe integer);")


def custom(dbpath, command):
	"execute a custom query on specified db"
	
	conn = dbconnect(dbpath)
	
	cursor = conn.cursor()
	queryOut = cursor.execute(command).fetchall()
	
	if(len(queryOut) > 0):
		for query in queryOut:
			print query
			
	
	conn.commit()
	conn.close()
	
	return 'Done'	

	
#get path to db	
dbpath = raw_input('Path to database? ')
while 1:
    command = raw_input('Enter SQLite3 query to run: ')
    finished = custom(dbpath, command)

print finished
