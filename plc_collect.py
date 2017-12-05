import RPi.GPIO as GPIO
import socket
import pytz
import time
from time import gmtime, strftime, sleep
import datetime
import urllib3
http = urllib3.PoolManager()
import logging
import urllib2
import sys
import ConfigParser
import uuid
#for python 2
import urllib
import threading
#for python 3
#from urllib.parse import urlencode
import buffer
from time import gmtime, strftime, sleep
import datetime
import Queue
machineName =[]
machineCycleSignal=[]
machineGoodbadPartSignal=[]
q=Queue.Queue(maxsize=10)
config = ConfigParser.ConfigParser()
config.optionxform = str
config.readfp(open(r'machineConfig.txt'))
path_items = config.items( "machine-config" )
LOCATION=None
for key, value in path_items:
        if 'Facility'in key:
                LOCATION = value
        if 'TotalMachines' in key:
                totalMachines=int(value)
        if 'MACHINE' in key:
                machineName.append(value)
        if 'CYCLE' in key:
                machineCycleSignal.append(int (value))
        if '_Quality' in key:
                        if key == machineName[-1]+"_Quality":
                                if value !="not connected":
                                        machineGoodbadPartSignal.append(int(value))
                                else:
                                        machineGoodbadPartSignal.append(0)


log_config = ConfigParser.ConfigParser()
log_config.readfp(open(r'logConfig.txt'))

LOG= log_config.get('log-config', 'LOG_ENABLE')
HOST=log_config.get('log-config', 'REMOTE_HOST')
PORT=log_config.get('log-config', 'REMOTE_PORT')
#lock=threading.Lock()
root = logging.getLogger()
root.setLevel(logging.DEBUG)
if LOG == 'True':
        root.disabled = False
else :
        root.disabled=True
log_message =logging.StreamHandler(sys.stdout)
log_message.setLevel(logging.DEBUG)
#use %(lineno)d for printnig line  no
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',"%Y-%m-%d %H:%M:%S")
#formatter = logging.Formatter('%(levelname)s : %(message)s')
log_message.setFormatter(formatter)
root.addHandler(log_message)

logging.debug(machineGoodbadPartSignal)
logging.debug(machineCycleSignal)
logging.debug(LOCATION)

machine1_good_badpart_pinvalue=0
machine1_cycle_risingEdge_detected=0
machine2_good_badpart_pinvalue=0
machine2_cycle_risingEdge_detected=0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for setupPinAsInput in range(len(machineCycleSignal)):
        logging.debug( "setting pin %d as input ",machineCycleSignal[setupPinAsInput])
        GPIO.setup(machineCycleSignal[setupPinAsInput], GPIO.IN, pull_up_down=GPIO.PUD_UP)

for setupPinAsInput in range(len(machineGoodbadPartSignal)):

        if machineGoodbadPartSignal[setupPinAsInput]!=0 :
                logging.debug( "setting pin %d as input ",machineGoodbadPartSignal[setupPinAsInput])
                GPIO.setup(machineGoodbadPartSignal[setupPinAsInput], GPIO.IN, pull_up_down=GPIO.PUD_UP)


#INITALIZE = 1
## PIN NUBERS   BCM  PHYCICAL
#               27    13
#               18   12
#GPIO.setup(0, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(18, GPIO.OUT, pull_up_down = GPIO.PUD_UP)



class Machine:
        'Common base class for all machines'
        MachineCount = 0
        def __init__(self, machine_cycle_rising_edge, machine_cycle_falling_edge, machine_cycle_pulse_time):
                self.machine_cycle_rising_edge = machine_cycle_rising_edge
                self.machine_cycle_falling_edge = machine_cycle_falling_edge
                self.machine_cycle_pulse_time = machine_cycle_pulse_time

                #Machine.machineCount += 1
        def machine_cycle_starttime(self):

                self.machine_cycle_rising_edge=time.time()
 #               logging.debug(self.machine_cycle_rising_edge)
        def machine_cycle_stoptime(self):
                self.machine_cycle_falling_edge=time.time()
#                logging.debug(self.machine_cycle_falling_edge)
        def machine_cycle_cleartime(self):
                self.machine_cycle_rising_edge=0
                self.machine_cycle_falling_edge=0
        def machine_cycle_pulseTime(self,machinename):
                self.machinename=machinename
                self.machine_cycle_pulse_time=self.machine_cycle_falling_edge-self.machine_cycle_rising_edge
                logging.debug ("Total Duration of MACHINE CYCLE SIGNAL for %s :%s ",machinename,str(self.machine_cycle_pulse_time))
                if self.machine_cycle_pulse_time >=2 and self.machine_cycle_pulse_time <= 4 :
                        return 1
                else:
                        return 0

def sendData(timestamp,machinename,data):
        data_send_from_machine_status=0
        fields={'ts':timestamp,'loc':LOCATION,'mach':machinename,'data':data}
        encoded_args = urllib.urlencode(fields)
        url = 'http://' + HOST + ':' + PORT + '/get?' + encoded_args
        try:
                r = http.request('GET', url,timeout=2.0)
                data_send_from_machine_status=r.status
        except urllib3.exceptions.MaxRetryError as e:
                data_send_from_machine_status=0
        if data_send_from_machine_status==0 or data_send_from_machine_status != 200 :
                if data_send_from_machine_status==0:
                        logging.error(" Not able to send data : Connection Error")
                else:
                        logging.debug("HTTP send status : %d",data_send_from_machine1_status)
                buffer.push(timestamp+" "+LOCATION+ " " + machinename +" "+data)
        else:
                logging.debug("HTTP send status : %d",data_send_from_machine_status)


def internet_on():
        #host ='52.170.42.16'
        #port = 5555
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
                s.connect((HOST, int(PORT)))
                s.close()
                return True
        except:
                return False
def plcMachine1(channel):
        time.sleep(0.1)
        global q
        global machine1_cycle_risingEdge_detected
        global machine1_good_badpart_pinvalue
        global LOCATION
        data_send_from_machine1_status=0
        machine1_cycle_pinvalue=0
        if (GPIO.input(machineCycleSignal[0])==0): # dry contact closed on machine cycle pin
                machine1_cycle_risingEdge_detected = 1
                #m1.machine_cycle_starttime()
                logging.debug ("Rising edge : %s Cycle Signal ",machineName[0])
                m1.machine_cycle_starttime()
                if (GPIO.input(machineGoodbadPartSignal[0])==0): # check value of good_badpart_signal and set it to 1 if ok
                        machine1_good_badpart_pinvalue=1
                else:   #good_badpart is not ok
                        machine1_good_badpart_pinvalue=0
        else: # dry contact opend falling edge detected for machine_cycle pin
                if machine1_cycle_risingEdge_detected == 1:
                        logging.debug ("Falling edge : %s Cycle Signal ",machineName[0])
                        m1.machine_cycle_stoptime()
                        machine1_cycle_risingEdge_detected=0
                        #utc_datetime = datetime.datetime.utcnow()
                        machine_cycle_timestamp=datetime.datetime.now(tz=pytz.UTC).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+"+00:00"
                        machine1_cycle_pinvalue=m1.machine_cycle_pulseTime(machineName[0])
                        if machine1_cycle_pinvalue==1:                          #//if this is valid pulse
                                if(GPIO.input(machineGoodbadPartSignal[0])==0):
                                        machine1_good_badpart_pinvalue=1
                                else:
                                        machine1_good_badpart_pinvalue=0
                                finalmessage="Quality"+":"+str(machine1_good_badpart_pinvalue)
                                logging.debug(finalmessage)
                        #        sendData(machine_cycle_timestamp,machineName[0],finalmessage)
                                send_message=machine_cycle_timestamp+" "+machineName[0]+" "+finalmessage
                                q.put(send_message)
                                q.task_done()
#                               print q.qsize()
                        else:
                                logging.debug(" %s cycle pulse width is invalid",machineName[0])
                m1.machine_cycle_cleartime()
                        #machine_cycle_risingEdge_detected = 0


def plcMachine2(channel):
        global q
        time.sleep(0.1)
        global machine2_cycle_risingEdge_detected
        global machine2_good_badpart_pinvalue
        global LOCATION
        data_send_from_machine2_status=0
        machine2_cycle_pinvalue=0
        if (GPIO.input(machineCycleSignal[1])==0): # dry contact closed on machine cycle pin
                machine2_cycle_risingEdge_detected = 1
                logging.debug ("Rising edge : %s Cycle Signal ",machineName[1])
                m2.machine_cycle_starttime()
                if (GPIO.input(machineGoodbadPartSignal[1])==0): # check value of good_badpart_signal and set it to 1 if ok
                        machine2_good_badpart_pinvalue=1
                else:   #good_badpart is not ok
                        machine2_good_badpart_pinvalue=0
        else: # dry contact opend falling edge detected for machine_cycle pin
                if machine2_cycle_risingEdge_detected == 1:
                        logging.debug ("Falling edge : %s Cycle Signal ",machineName[1])
                        m2.machine_cycle_stoptime()
                        machine2_cycle_risingEdge_detected=0
                        #utc_datetime = datetime.datetime.utcnow()
                        machine_cycle_timestamp=datetime.datetime.now(tz=pytz.UTC).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+"+00:00"
                        machine2_cycle_pinvalue=m2.machine_cycle_pulseTime(machineName[1])
                        if machine2_cycle_pinvalue==1:
                                if(GPIO.input(machineGoodbadPartSignal[1])==0): # valid pulse
                                        machine2_good_badpart_pinvalue=1
                                else:
                                        machine1_good_badpart_pinvalue=0
                                #try:
                                #        lock.acquire()
                                finalmessage="Quality"+":"+str(machine2_good_badpart_pinvalue)
                                logging.debug(finalmessage)
                                send_message=machine_cycle_timestamp+" "+machineName[1]+" "+finalmessage
                                q.put(send_message)
                                q.task_done()
#                               print q.qsize()
#                               print q.get()
                                #sendData(machine_cycle_timestamp,machineName[1],finalmessage)
                        else:
                                logging.debug(" %s cycle pulse width is invalid",machineName[1])
                m2.machine_cycle_cleartime()





def get_mac():
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
        return mac

mac=str(get_mac())

plcMachine = lambda totalMachines: eval("plcMachine"+str(totalMachines))
#print plcMachine(1)
for addDetectionOnPin in range (totalMachines):
        logging.debug( "added detection on pin no : %d",machineCycleSignal[addDetectionOnPin])
        GPIO.add_event_detect(machineCycleSignal[addDetectionOnPin], GPIO.BOTH, callback=plcMachine(addDetectionOnPin+1),bouncetime=200)
#GPIO.add_event_detect(MACHINE2_CYCLE, GPIO.BOTH, callback=plcMachine2,bouncetime=200)

m1 = Machine(0, 0, 0)
m2 = Machine(0, 0, 0)

def machineData(q):
        logging.debug("machine thread started")
        messagesSinceLastReboot=0
        fd = open("testfile.txt", "r+")
        totalMessage=int(fd.read())
        fd.close()
        while True:
                data=q.get()
                messagesSinceLastReboot= messagesSinceLastReboot+1
                totalMessage=totalMessage+1
                logging.info("Local Message Received since last Reboot :%d",messagesSinceLastReboot)

                fd = open("testfile.txt", "w+")
                fd.write(str(totalMessage))
                fd.close()
                dataToSend=data.split()
                #logging.debug("need to send this data")
                #logging.debug(dataToSend)
                sendData(dataToSend[0],dataToSend[1],dataToSend[2])
        logging.debug("machine data exited")


t = threading.Thread(name = "sendDataThread", target=machineData, args=(q,))
t.start()
#print ("Total machines  %d" % Machine.machineCount)
logging.debug("data collection started")
try:
        while True:
                if internet_on()==True:
                        logging.debug( " Connection status to nifi : CONNECTED ")
                        data=buffer.pop().rstrip()
                        if data!="-1":
                                while data!="-1":
                                        dataTosend=data.split()
                                        #logging.debug(dataTosend)
                                        if len(dataTosend)!=0:
                               #print "poping element"
                                                sendData(dataTosend[0],dataTosend[2],dataTosend[3])
                                                time.sleep(3)
                                                data=buffer.pop().rstrip()
                       # else:
                                #logging.debug( " No local messages")
                else:
                        logging.error(" Connection status to nifi : NO NETWORK ")
                time.sleep(60)
#        logging.debug("--")
except KeyboardInterrupt:
        logging.debug(" Quit ")
        GPIO.cleanup()
