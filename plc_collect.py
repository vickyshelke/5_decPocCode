import RPi.GPIO as GPIO
import time
from time import gmtime, strftime, sleep
import datetime
import urllib3
http = urllib3.PoolManager()
import logging
import sys
import ConfigParser
import uuid
#for python 2
import urllib
import threading
#for python 3
#from urllib.parse import urlencode
import buffer
config = ConfigParser.ConfigParser()
config.readfp(open(r'config.txt'))
MACHINE1_CYCLE  = int(config.get('machine-config', 'MACHINE1_CYCLE'))
MACHINE1_GOOD_BAD =int(config.get('machine-config','MACHINE1_GOOD_BAD'))
MACHINE2_CYCLE  = int(config.get('machine-config', 'MACHINE2_CYCLE'))
MACHINE2_GOOD_BAD =int(config.get('machine-config','MACHINE2_GOOD_BAD'))
TOTAL_MACHINE_CONNECTED = int(config.get('machine-config', 'TOTAL_MACHINES_CONNECTED'))
LOG             = config.get('machine-config', 'LOG_ENABLE')
#if MACHINE1_GOOD_BAD=="NOT CONNECTED":

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
log_message.setFormatter(formatter)
root.addHandler(log_message)


machine1_good_badpart_pinvalue=0
machine1_cycle_risingEdge_detected=0
machine2_good_badpart_pinvalue=0
machine2_cycle_risingEdge_detected=0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
#MACHINE_CYCLE  = 23
#MACHINE_CYCLE2 = 24
#GPIO.setup(MACHINE_CYCLE,GPIO.IN)
#GPIO.setup(MACHINE_CYCLE2,GPIO.IN)

GPIO.setup(MACHINE1_CYCLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MACHINE1_GOOD_BAD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MACHINE2_CYCLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MACHINE2_GOOD_BAD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(STATUS1,GPIO.OUT)
#GPIO.setup(STATUS2,GPIO.OUT)

#INITALIZE = 1
## PIN NUBERS   BCM  PHYCICAL
#               27    13
#               18   12
#GPIO.setup(0, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(18, GPIO.OUT, pull_up_down = GPIO.PUD_UP)



class Machine:
        'Common base class for all machines'
        machineCount = 0
        def __init__(self, machine_cycle_rising_edge, machine_cycle_falling_edge, machine_cycle_pulse_time,totalParts):
                self.machine_cycle_rising_edge = machine_cycle_rising_edge
                self.machine_cycle_falling_edge = machine_cycle_falling_edge
                self.machine_cycle_pulse_time = machine_cycle_pulse_time
                self.totalParts=totalParts
                Machine.machineCount += 1
        def machine_cycle_starttime(self):
                self.machine_cycle_rising_edge=time.time()
        def machine_cycle_stoptime(self):
                self.machine_cycle_falling_edge=time.time()
        def machine_cycle_cleartime(self):
                self.machine_cycle_rising_edge=0
                self.machine_cycle_falling_edge=0
        def machine_cycle_pulseTime(self):
                self.machine_cycle_pulse_time=self.machine_cycle_falling_edge-self.machine_cycle_rising_edge
                logging.debug ("Total Duration of MACHINE CYCLE SIGNAL is :%s ",str(self.machine_cycle_pulse_time))
                if self.machine_cycle_pulse_time >=2 and self.machine_cycle_pulse_time <= 4 :
                        return 1
                else:
                        return 0


def plcMachine1(channel):
        time.sleep(0.1)
        global machine1_cycle_risingEdge_detected
        global machine1_good_badpart_pinvalue
	data_send_from_machine1_status=0
	machine1_cycle_pinvalue=0
        if (GPIO.input(MACHINE1_CYCLE)==0): # dry contact closed on machine cycle pin
                machine1_cycle_risingEdge_detected = 1
                m1.machine_cycle_starttime()
                logging.debug ("Rising edge : MACHINE CYCLE SIGNAL ")
                if (GPIO.input(MACHINE1_GOOD_BAD)==0): # check value of good_badpart_signal and set it to 1 if ok
                        machine1_good_badpart_pinvalue=1
                else:   #good_badpart is not ok
                        machine1_good_badpart_pinvalue=0
        else: # dry contact opend falling edge detected for machine_cycle pin
                if machine1_cycle_risingEdge_detected == 1:
                        m1.machine_cycle_stoptime()
                        machine1_cycle_risingEdge_detected=0
                        utc_datetime = datetime.datetime.utcnow()
                        machine_cycle_timestamp=utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        #machine_cycle_timestamp  = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        #logging.info(machine_cycle_timestamp)
                        logging.debug ("Falling edge: MACHINE CYCLE SIGNAL ")
                        machine1_cycle_pinvalue=m1.machine_cycle_pulseTime()
                        machine2_cycle_pinvalue=0
                        machine2_good_bad=0
                        if(GPIO.input(MACHINE2_CYCLE)==0):
                                machine2_cycle_pinvalue=1
                        else:
                                machine2_cycle_pinvalue=0
                        if(GPIO.input(MACHINE2_GOOD_BAD)==0):
                                machine2_good_bad=1
                        else:
                                machine2_good_bad=0
                        #try:
                        #        lock.acquire()
                        finalmessage=str(MACHINE1_CYCLE)+":"+str(machine_cycle_pinvalue)+"|"+str(MACHINE1_GOOD_BAD)+":"+str(good_badpart_pinvalue)+"|"+str(MACHINE2_CYCLE)+":"+str(machine2_cycle_pinvalue)+"|"+str(MACHINE2_GOOD_BAD)+":"+str(machine2_good_bad)
                        logging.debug(finalmessage)
                        fields={'ts':machine_cycle_timestamp,'loc':"izmir",'mac':mac,'data':finalmessage}
                        encoded_args = urllib.urlencode(fields)
                        url = 'http://52.170.42.16:5555/get?' + encoded_args
                        try:
                                r = http.request('GET', url,timeout=1.0)
                                data_send_from_machine1_status=r.status
                                #logging.debug('HTTP Send Status: ',r.status)
                        except urllib3.exceptions.MaxRetryError as e:
                                data_send_from_machine1_status=0
                        #print('connection error: ')
                        if data_send_from_machine1_status==0 or data_send_from_machine1_status != 200 :
                                logging.debug("not able to send data connection error")
                                buffer.push(machine_cycle_timestamp+" "+mac+" IZMIR "+finalmessage)
                        else:
                                logging.debug("HTTP send status : %d",data_send_from_machine1_status)
                        m1.machine_cycle_cleartime()
                        #machine_cycle_risingEdge_detected = 0
                        

def PlcMachine2(channel):
        time.sleep(0.1)
        global machine2_cycle_risingEdge_detected
        global machine2_good_badpart_pinvalue
	data_send_from_machine2_status=0
	machine2_cycle_pinvalue=0
        if (GPIO.input(MACHINE2_CYCLE)==0): # dry contact closed on machine cycle pin
                machine2_cycle_risingEdge_detected = 1
                m2.machine_cycle_starttime()
                logging.debug ("Rising edge : MACHINE CYCLE SIGNAL ")
                if (GPIO.input(MACHINE2_GOOD_BAD)==0): # check value of good_badpart_signal and set it to 1 if ok
                        machine2_good_badpart_pinvalue=1
                else:   #good_badpart is not ok
                        machine2_good_badpart_pinvalue=0
        else: # dry contact opend falling edge detected for machine_cycle pin
                if machine2_cycle_risingEdge_detected == 1:
                        m2.machine_cycle_stoptime()
                        machine2_cycle_risingEdge_detected=0
                        utc_datetime = datetime.datetime.utcnow()
                        machine_cycle_timestamp=utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        #machine_cycle_timestamp  = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        #logging.info(machine_cycle_timestamp)
                        logging.debug ("Falling edge: MACHINE CYCLE SIGNAL ")
                        machine2_cycle_pinvalue=m1.machine_cycle_pulseTime()
                        machine1_cycle_pinvalue=0
                        machine1_good_bad=0
                        if(GPIO.input(MACHINE1_CYCLE)==0):
                                machine1_cycle_pinvalue=1
                        else:
                                machine2_cycle_pinvalue=0
                        if(GPIO.input(MACHINE1_GOOD_BAD)==0):
                                machine1_good_bad=1
                        else:
                                machine1_good_bad=0
                        #try:
                        #        lock.acquire()
                        finalmessage=str(MACHINE2_CYCLE)+":"+str(machine2_cycle_pinvalue)+"|"+str(MACHINE2_GOOD_BAD)+":"+str(machine2_good_badpart_pinvalue)+"|"+str(MACHINE1_CYCLE)+":"+str(machine1_cycle_pinvalue)+"|"+str(MACHINE1_GOOD_BAD)+":"+str(machine1_good_bad)
                        logging.debug(finalmessage)
                        fields={'ts':machine_cycle_timestamp,'loc':"izmir",'mac':mac,'data':finalmessage}
                        encoded_args = urllib.urlencode(fields)
                        url = 'http://52.170.42.16:5555/get?' + encoded_args
                        try:
                                r = http.request('GET', url,timeout=1.0)
                                data_send_from_machine2_status=r.status
                                #logging.debug('HTTP Send Status: ',r.status)
                        except urllib3.exceptions.MaxRetryError as e:
                                data_send_from_machine2_status=0
                        #print('connection error: ')
                        if data_send_from_machine2_status==0 or data_send_from_machine2_status != 200 :
                                logging.debug("not able to send data connection error")
                                buffer.push(machine_cycle_timestamp+" "+mac+" IZMIR "+finalmessage)
                        else:
                                logging.debug("HTTP send status : %d",data_send_from_machine2_status)
                        m2.machine_cycle_cleartime()





def get_mac():
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
        return mac

mac=str(get_mac())


GPIO.add_event_detect(MACHINE1_CYCLE, GPIO.BOTH, callback=plcMachine1,bouncetime=200)
GPIO.add_event_detect(MACHINE2_CYCLE, GPIO.BOTH, callback=plcMachine2,bouncetime=200)
m1 = Machine(0, 0, 0, 0)
m2 = Machine(0, 0, 0, 0)
#print ("Total machines  %d" % Machine.machineCount)
logging.debug("data collection started")
try:
        while True:
                time.sleep(10)
                logging.debug("--")
except KeyboardInterrupt:
        logging.debug("Quit")
        GPIO.cleanup()

