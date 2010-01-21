'''
auto.py

~~~~~~~~~~~~~~~~~~~~~~~
Written with Python 2.6 and pySerial (http://pyserial.sourceforge.net/)
	for Clark Solutions

By David Tyler
~~~~~~~~~~~~~~~~~~~~~~~

This script automates the calibration process on the lowflow test bench.
It does this by first collecting information from the operator (Customer,SN,...),
then setting up the datalogger and taking data. A config file (parameters.h)
is then generated to setup important varables. The data is read out,
and a new K is calculated. The config file is then modified to set the new K.
Two more runs of data are taken and if the data is good, a report is generated (HTML)
and displayed, and both the report and the config file are moved to another directory
and renamed by the meter's SN_PCBSN.h (or .html)


~~~~~~~~~~~~~~~~~~~~~~
Operator Steps:
	Open the custom MPLAB project
	Follow on-screen prompts to enter information
	When prompted, compile and upload the MPLAB project
	Release the meter from reset
	Press Enter to resume operation of this script
	Wait for script to finish getting data
	When prompted, compile and upload the MPLAB project
	Release the meter from reset
	Press Enter to resume operation of this script
	The script will now take 2 more sets of data and automatically open a report
	Print the report that opens, then close it
	Done
~~~~~~~~~~~~~~~~~~~~~~


~~~~~~~~~~~~~~~~~~~~~~
NOTES:
	Currently, this script operated in the C:\cal folder. Create this if it does not exist.
	You need to download and install Python 2.6 from python.org
	You need to download and install pySerial from http://pyserial.sourceforge.net/
	If the operator enters any information incorrectly, the script must be restarted from the beginning.
	This script and all associated materials reside in a Mercurial repository at http://bitbucket.org/ipsum/calibration-script/overview/
	For information on regex (regular expressions) look up the re module on python.org in the 2.6 documentation and also look at en.wikipedia.org/wiki/Regular_expression
	
	
'''


from __future__ import division
import serial
import os
import re
import time
import datetime

#dictionary of size index->FS(lowG,highG,lowL,highL,Default_K)
#Example: sizeFS[size_index][0] returns the low fullscale in gallons for a given size index. sizeFS[2][0] returns 40
sizeFS = {0: [15,25,60,100,.86], 1: [30,50,115,200,.92], 2: [40,80,150,300,3.25], 3: [60,120,225,455,3.26]}
#Dictionary to map possible inputs to values. resp['y'] is 1 (meaning yes).
resp   = {'y': 1, 'Y': 1, 'n': 0, 'N': 0}

#functions

#Values writted to serial port copied from the ALMEMO 2690 documentation
def setup(FS):
        s = serial.Serial(0) #Open serial port(using defaults: 9700 baud, port 0, ect) and create a serial port object called s
        s.write("E00")  #Write E00 to open serial port (selects channel M00)
        s.write("f1")
        s.write("k0") #locking mode 0
        s.write('F{0}'.format(float(FS/1000))) #Set full scale (the float FS/1000 replaces {0}) (This is the same as printf("something %d", arg))
        s.write('0000') #write enough 0's to fill buffer so fullscale will be accepted
        print 'FS: {0}'.format(float(FS/1000)) #debug output to console
        s.write("f1")
        s.write("k7") #locking mode 7
        s.write("N2") #spreadsheet mode
		
		#flushes are unnecessary but added for robustness. Clears any data that might be waiting to be sent or received from serial port.
        s.flushInput() 
        s.flushOutput()
        s.close() #close the serial connection

        return s.isOpen() #check to see if the serial connection is open and make this the return value of the function

def getdata():
        
        REFavg   = 0
        MUTavg   = 0
        step     = 10 #10 sec per measurement
        timec    = 20 #total measurement run in sec
        
        #ser = serial.Serial()
        #ser.baudrate = 9600
        #ser.port = 0
        
        div = timec/step

        p = re.compile('-?[0-9]*,[0-9]*') #regex (regular expression) to format input. Matches 23,1 and 1,1 and 2, and ,6 and -23,1 Using this to grab the averages from a line of datalogger data.
        
        ser = serial.Serial(0) #create a new serial object called ser
        ser.flushInput()
        ser.flushOutput()
        
        print ser.isOpen()

        while timec > 0:
                
                ser.write('S1')  #get one line of data
                rLn = ser.readline() #discard first line of junk
                rLn = ser.readline() #read line of data and store it as a string in rLn
                print str(rLn)	#print rLn to console for debug output
                s = p.findall(rLn) #Find every substring in rLn that matched the regex p and store it in the array s. It finds the MUT average and REF average in that order.
                
				#Since the datalogger is german, commas are used instead of periods to deliminate the ones and tenths places.
				#So, we replace all of the commas by periods in each string in the array and convert both strings to floats
                MUT = float(s[0].replace(",","."))
                REF = float(s[1].replace(",","."))
                if MUT < 0 or REF < 0: #check to make sure greater than zero flow is being reported, otherwise throw an error and discard this data until operator fixes
                        raw_input('Meter in reset, fix and hit enter.')
                        timec += step #add the time this step took back to the counter
                        REF = 0
                        MUT = 0
                print 'Diff: ' + str(MUT-REF) #print the differences between the averages for each run
                REFavg += REF
                MUTavg += MUT
                
                timec -= step
                time.sleep(step) #wait for step seconds
               
        REFavg /= div
        MUTavg /= div
        
        ser.close()
        
        print 'MUT Avg ' + str(MUTavg) + ' REF Avg: ' + str(REFavg) #print this concated string
        return [MUTavg,REFavg] #return the array containing the MUT avg and the REF avg
        
def endprog(): #This is never called, just here in case I decide I need it some time in the future
        ser.close()
        print 'goodbye'
        os._exit(99)
        
#lets establish known information
print 'Clark Solutions Calibration Automation Program'

customer  = raw_input('Customer name? ') #raw_input prints a message then waits for input to be entered followed by a newline. It stores the input to a varible
patt      = re.compile('[^A-Za-z \t].') #regex matches all invalid customer name patterns
while patt.search(customer):
        customer = raw_input('Invalid Customer name, please enter again ')
        
wOrder    = raw_input('Work order #? ')
patt      = re.compile('[^Oo0-9].')
while patt.search(wOrder):
        wOrder = raw_input('Invalid Order #, please enter again ')
        
castingSN = raw_input('Casting SN? ')
patt      = re.compile('[^0-9].')
while patt.search(castingSN):
        castingSN = raw_input('Invalid SN, please enter again ')
        
pcbSN     = raw_input('PCB SN? ')
patt      = re.compile('[^0-9].')
while patt.search(pcbSN):
        pcbSN = raw_input('Invalid SN, please enter again ')
        
dz        = raw_input('DZ? ')
patt      = re.compile('[^0-9.].') #need to escape . ?
while patt.search(dz):
        dz = raw_input('Invalid DZ, please enter again ')
        
fe        = raw_input('First Echo (mV)? ')
patt      = re.compile('[^0-9].')
while patt.search(fe):
        fe = raw_input('Invalid FE, please enter again ')
        
pol       = raw_input('Complemented Polarity? [y/n] ') 
patt      = re.compile('[^YNyn].') #this regex is wrong, need to match: Start of line [YNyn]
while patt.search(pol):
        pol = raw_input('Invalid Polarity, please enter y or n\n Complemented Polarity? [y/n] ')
pol       = resp[pol[0]] #looks up the first character of the input string (in case they type out "Yes" instead of "y") in the resp dictionary. It saves the 1 or 0 that is returned in the pol varible
        
size      = int(raw_input('Size Index? (0 = 3/4", 1 = 1", ect) '))
liter     = raw_input('Liters? [y/n] ')
liters    = resp[liter[0]]+1 #the +1 makes a the lowFS and highFS formulas work
df        = raw_input('Direction of Flow? [y/n] ')
pulse     = raw_input('Pusle input? [y/n] ')
custFS    = raw_input('Custom Fullscale? [y/n] ')

if resp[custFS[0]]:
        highFS = int(raw_input('High FS? '))
        lowFS  = int(raw_input('Low FS? '))
else:
        lowFS  = sizeFS[size][(liters-1)*2] #magic formulas to get the correct fullscale
        highFS = sizeFS[size][(liters*2)-1]

K = sizeFS[size][4] #retreive the default K value from the sizeFS dictionary

f = open(r'C:\cal\parameters.h','w') #open parameters.h in w mode (creates file if does not exist, otherwise deletes existing file by the same name and creates a new one. Opens file in write mode)

f.write('#define K_auto {0}\n'.format(K)) # K replaces {0} (This is the same as printf("something %d", arg))
f.write('#define DZ_auto {0}\n'.format(dz))

if resp[df[0]]: #if the first character of the string df is Y or y, the resp dictionary returns 1, making this if statement true
        f.write('#define _DIR\n')
if resp[pulse[0]]:
        f.write('#define _PULSE\n')
f.write('#define _lowFS {0}\n'.format(str(lowFS)))
f.write('#define _highFS {0}\n'.format(str(highFS)))
f.close()

#Setup for data run (datalogger settings/operator setup)
setup(highFS) #calls the setup function defined at def setup(fs):

#Compile,link,upload
        #ok I can do the compile&link but have no cli uploader so we will ask the operator to do this for us
raw_input('Please compile and upload the program with the updated code module')


#take data
average = getdata() #calls the getdata function and stores the return value array [MUTavg,REFavg] in average

#check data
if average[0]<5 and average[1]>5:
        print 'Possible setup error, please check for fault and power and flow'
        
if not 0 < average[0] < highFS: #if MUTavg is not between 0 and highFS print an error
        print 'Average out of range'
        
#new K (K*REFavg)/MUTavg
K = (K*average[1])/average[0]
f = open(r'C:\cal\parameters.h','a') #Append mode ('a') opens and existing file for writing and starts writing at the end of the file without erasing any existing data
f.write('//MUT Avg: {0}, REF Avg: {1}\n'.format(average[0],average[1])) #print a commented out line containing the most recent averages to config file
f.write('#define K_auto {0}\n'.format(K)) #write the new K to the config file
f.close()

#compile,link,upload
raw_input('Recompile and upload')

#5 min data
average = getdata()

#check data
if average[0]<5 and average[1]>5:
        print 'Possible setup error, please check for fault and power and flow'
        
if not 0 < average[0] < highFS:
        print 'Average out of range'
        
err = (average[1]-average[0])*100/highFS
if err>1.5:
        print 'Error>1.5'

#save data
avg1 = average #save the average for use in our report later

f = open(r'C:\cal\parameters.h','a') #append mode
f.write('//MUT Avg: {0}, REF Avg: {1}\n'.format(average[0],average[1]))
f.close()

#setup for different flowrate
raw_input('Change Flow')

#5min data
average = getdata()

#check data
if average[0]<5 and average[1]>5:
        print 'Possible setup error, please check for fault and power and flow'
        
if not 0 < average[0] < highFS:
        print 'Average out of range'
        
err = (average[1]-average[0])*100/highFS
if err>1.5:
        print 'Error>1.5'
        
#save data
avg2 = average #save the average for use in our report later

f = open(r'C:\cal\parameters.h','a') #append mode
f.write('//MUT Avg: {0}, REF Avg: {1}\n'.format(average[0],average[1]))
f.close()

#create report by writing some html
d = datetime.date.today() #gets today's current date from the datetime module
r = open(r'C:\cal\report.html','w') #create a report file
r.write('<html><body><h1>{0} {1}</h1>\n<p>Casting: {2} PCB: {3}<BR><BR>DZ: {4} FE: {5}<BR><BR>K: {6}<BR><BR>Polarity {7}'.format(customer,wOrder,castingSN,pcbSN,dz,fe,K,pol))
r.write('<BR><BR><h2>Run 1</h2><p2>MUT: {0} REF: {1}<BR><BR>Error: {2}</p2><BR><BR><h2>Run 2</h2><p2>MUT: {3} REF: {4}<BR><BR>Error: {5}'.format(avg1[0],avg1[1],(avg1[1]-avg1[0])*100/highFS,avg2[0],avg2[1],(avg2[1]-avg2[0])*100/highFS))
r.write('<BR><BR><BR>' + d.strftime("%m/%d/%Y")) #strftime formats the datetime object d that has today's current date. Outputting in mm/dd/YYYY format in this case.
r.close()

#move and rename parameters.c to backup directory (name as castingSN_pcbSN.c)
os.system('copy C:\\cal\\report.html C:\\cal\\data\\' + castingSN + '_' + pcbSN + '.html' + ' /Y') #copy and rename report.html to cal\data
os.system('copy C:\\cal\\parameters.h C:\\cal\\data\\' + castingSN + '_' + pcbSN + '.h' + ' /Y') #copy and rename parameters.h to cal\data
os.system('C:\\cal\\data\\' + castingSN + '_' + pcbSN + '.html') #open the copied report for printing
