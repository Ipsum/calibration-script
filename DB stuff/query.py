'''
query.py

Interface for looking up clarksonic records
'''

import os
import sqlite3
import webbrowser

dbpath = "ClarkSonic.db"

def dbconnect(db):
	"Connect to existing database"
	conn = sqlite3.connect(db)
	
	conn.commit()
	return conn
	
print "Clarksonic database lookup tool\n"
os.system('title Database Query')

print "Enter known parameters, otherwise leave blank\n"

customer = raw_input('Customer name: ')
so = raw_input('Sales Order Number: ')
pcb = raw_input('PCB SN: ')
casting = raw_input('Casting SN: ')
#date = raw_input('Date [mm/dd/yyyy]: ')

command = "select * from clarksonic where"
if customer:
	command += " customer=?"
	data = customer
if so:
	command += " salesorder=?"
	data = so
if pcb:
	command += " pcb=?"
	data = pcb
if casting:
	command += " casting=?"
	data = casting
#if date:
#	command += " date=?"

print command
conn = dbconnect(dbpath)
entries = conn.execute(command, (data,)).fetchall()

r = open(r'report.html','w') #create a report file
r.write('<html><body>')
for entry in entries:
	r.write('<h1>Casting SN {0} </h1>\n<p>Sales Order: {2}<BR><BR>Customer: {1}<BR> PCB SN: {3} <BR><BR>K: {6}<BR>DZ: {4} <BR><BR>FE: {5}<BR>Polarity: {7}</p>'.format(entry[4],entry[1],entry[2],entry[3],entry[8],entry[13],entry[7],entry[9]))

r.write('</body></html>')
r.close()

webbrowser.open_new_tab('report.html')
