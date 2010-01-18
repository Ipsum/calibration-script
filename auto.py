from __future__ import division
import serial
import os
import re
import time
import datetime

#dictionary of size index->FS(lowG,highG,lowL,highL,Default_K)
sizeFS = {0: [15,25,60,100,.86], 1: [30,50,115,200,.92], 2: [40,80,150,300,3.25], 3: [60,120,225,455,3.26]}
resp   = {'y': 1, 'Y': 1, 'n': 0, 'N': 0}

#functions
def setup(FS):
        s = serial.Serial(0) #open serial port
        s.write("E00")  #channel M00
        s.write("f1")
        s.write("k0") #locking mode 0
        s.write('F{0}'.format(float(FS/1000))) #set full scale
        s.write('0000')
        print 'FS: {0}'.format(float(FS/1000))
        s.write("f1")
        s.write("k7") #locking mode 7
        s.write("N2") #spreadsheet mode
        s.flushInput()
        s.flushOutput()
        s.close()

        return s.isOpen()

def getdata():
        
        REFavg   = 0
        MUTavg   = 0
        step     = 10 #10 sec per measurement
        timec    = 20 #total measurement run in sec
        
        #ser = serial.Serial()
        #ser.baudrate = 9600
        #ser.port = 0
        
        div = timec/step

        p = re.compile('-?[0-9]*,[0-9]*') #regex to format input
        
        ser = serial.Serial(0)
        ser.flushInput()
        ser.flushOutput()
        
        print ser.isOpen()

        while timec > 0:
                
                ser.write('S1')  #get one line of data
                rLn = ser.readline() #discard echo
                rLn = ser.readline()
                print str(rLn)
                s = p.findall(rLn) #clean input
                
                MUT = float(s[0].replace(",","."))
                REF = float(s[1].replace(",","."))
                if MUT < 0 or REF < 0:
                        raw_input('Meter in reset, fix and hit enter.')
                        timec += step
                        REF = 0
                        MUT = 0
                print 'Diff: ' + str(MUT-REF)
                REFavg += REF
                MUTavg += MUT
                
                timec -= step
                time.sleep(step)
               
        REFavg /= div
        MUTavg /= div
        
        ser.close()
        
        print 'MUT Avg ' + str(MUTavg) + ' REF Avg: ' + str(REFavg)
        return [MUTavg,REFavg]
        
def endprog():
        ser.close()
        print 'goodbye'
        os._exit(99)
        
#lets establish known information
print 'Clark Solutions Calibration Automation Program'

customer  = raw_input('Customer name? ')
patt      = re.compile('[^A-Za-z \t].') #matches all invalid customer name patterns
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
        
pol       = resp[(raw_input('Complemented Polarity? [y/n] ')[0])]
patt      = re.compile('[YNyn].')
while patt.search(pol):
        pol = raw_input('Invalid Polarity, please enter y or n\n Complemented Polarity? [y/n] ')
        
size      = int(raw_input('Size Index? (0 = 3/4", 1 = 1", ect) '))
liter     = raw_input('Liters? [y/n] ')
liters    = resp[liter[0]]+1
df        = raw_input('Direction of Flow? [y/n] ')
pulse     = raw_input('Pusle input? [y/n] ')
custFS    = raw_input('Custom Fullscale? [y/n] ')

if resp[custFS[0]]:
        highFS = int(raw_input('High FS? '))
        lowFS  = int(raw_input('Low FS? '))
else:
        lowFS  = sizeFS[size][(liters-1)*2]
        highFS = sizeFS[size][(liters*2)-1]

K = sizeFS[size][4]

f = open(r'C:\cal\parameters.h','w')

f.write('#define K_auto {0}\n'.format(K))
f.write('#define DZ_auto {0}\n'.format(dz))

if resp[df[0]]:
        f.write('#define _DIR\n')
if resp[pulse[0]]:
        f.write('#define _PULSE\n')
f.write('#define _lowFS {0}\n'.format(str(lowFS)))
f.write('#define _highFS {0}\n'.format(str(highFS)))
f.close()

#Setup for data run (datalogger settings/operator setup)
setup(highFS)

#Compile,link,upload
        #ok I can do the compile&link but have no cli uploader so we will ask the operator to do this for us
raw_input('Please compile and upload the program with the updated code module')


#take data
average = getdata()

#check data
if average[0]<5 and average[1]>5:
        print 'Possible setup error, please check for fault and power and flow'
        
if not 0 < average[0] < highFS:
        print 'Average out of range'
        
#new K (K*REFavg)/MUTavg
K = (K*average[1])/average[0]
f = open(r'C:\cal\parameters.h','a') #append mode
f.write('//MUT Avg: {0}, REF Avg: {1}\n'.format(average[0],average[1]))
f.write('#define K_auto {0}\n'.format(K))
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
avg1 = average

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
avg2 = average

f = open(r'C:\cal\parameters.h','a') #append mode
f.write('//MUT Avg: {0}, REF Avg: {1}\n'.format(average[0],average[1]))
f.close()

#create report
d = datetime.date.today()
r = open(r'C:\cal\report.html','w')
r.write('<html><body><h1>{0} {1}</h1>\n<p>Casting: {2} PCB: {3}<BR><BR>DZ: {4} FE: {5}<BR><BR>K: {6}<BR><BR>Polarity {7}'.format(customer,wOrder,castingSN,pcbSN,dz,fe,K,pol))
r.write('<BR><BR><h2>Run 1</h2><p2>MUT: {0} REF: {1}<BR><BR>Error: {2}</p2><BR><BR><h2>Run 2</h2><p2>MUT: {3} REF: {4}<BR><BR>Error: {5}'.format(avg1[0],avg1[1],(avg1[1]-avg1[0])*100/highFS,avg2[0],avg2[1],(avg2[1]-avg2[0])*100/highFS))
r.write('<BR><BR><BR>' + d.strftime("%m/%d/%Y"))
r.close()

#move and rename parameters.c to backup directory (name as castingSN_pcbSN.c)
os.system('copy C:\\cal\\report.html C:\\cal\\data\\' + castingSN + '_' + pcbSN + '.html' + ' /Y')
os.system('copy C:\\cal\\parameters.h C:\\cal\\data\\' + castingSN + '_' + pcbSN + '.h' + ' /Y')
os.system('C:\\cal\\data\\' + castingSN + '_' + pcbSN + '.html')
