import RPi.GPIO as GPIO
import time
from time import gmtime, strftime, sleep
import urllib3
http = urllib3.PoolManager()


#for python 2
import urllib
#for python 3
#from urllib.parse import urlencode

import uuid


GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
MACHINE_CYCLE  = 23
STATUS1        = 18
MACHINE_CYCLE2 = 24
STATUS2        = 27
#GPIO.setup(MACHINE_CYCLE,GPIO.IN)
#GPIO.setup(MACHINE_CYCLE2,GPIO.IN)
GPIO.setup(MACHINE_CYCLE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(MACHINE_CYCLE2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(STATUS1,GPIO.OUT)
GPIO.setup(STATUS2,GPIO.OUT)

#INITALIZE = 1
## PIN NUBERS   BCM  PHYCICAL
#               27    13
#               18   12
#GPIO.setup(0, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(18, GPIO.OUT, pull_up_down = GPIO.PUD_UP)



class Machine:
        'Common base class for all machines'
        machineCount = 0
        def __init__(self, rising_edge, falling_edge, pulse_time,totalParts):
                self.rising_edge = rising_edge
                self.falling_edge = falling_edge
                self.pulse_time = pulse_time
                self.totalParts=totalParts
                Machine.machineCount += 1
        def starttime(self):
                self.rising_edge=time.time()
        def stoptime(self):
                self.falling_edge=time.time()
        def pulseTime(self):
                self.pulse_time=self.falling_edge-self.rising_edge
                print ("Total Duration of pulse is : "+str(self.pulse_time))
                self.totalParts += 1
                print ("total parts %d" % self.totalParts)
                if self.pulse_time >=2 and self.pulse_time <= 4 :#if pulse duration is ok part is good return value as 1
                        #print ("%d part is  good" % self.totalParts)
                        return 1
                else: #part is not ok return value 0
                        #print ("%d part is bad part" % self.totalParts)
                        return 0
def plcMachine1(channel):
        if GPIO.input(MACHINE_CYCLE): # if pin MACHINE_CYCLE == 1
                m1.starttime()
                print ("Rising edge detected on machine1 ")
                GPIO.output(STATUS1,GPIO.HIGH)
        else: # if pin MACHINE_CYCLE != 1
                m1.stoptime()
                now  = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                print ("falling edge detected on machine1")
                GPIO.output(STATUS1,GPIO.LOW)
                pinvalue=m1.pulseTime()
               # finalmessage=pinvalue+now+mac+str(pinvalue)
                fields={'g':pinvalue,'ts':now, 'mac': mac,'pin':27}
                encoded_args = urllib.urlencode(fields)
                url = 'http://52.170.42.16:5555/get?' + encoded_args
                try:
                        r = http.request('GET', url)
                        print('HTTP Send Status: ',r.status)
                except:
                        print('connection error: ')

def plcMachine2(channel):
                if GPIO.input(MACHINE_CYCLE2): # if pin MACHINE_CYCLE2 == 1
                        m2.starttime()
                        print   ("Rising edge  on machine2")
                        GPIO.output(STATUS2,GPIO.HIGH)
                else: # if pin MACHINE_CYCLE2 != 1
                        m2.stoptime()
                        print ("falling edge on machine2")
                        GPIO.output(STATUS2,GPIO.LOW)
                        m2.pulseTime()
                        now  = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        print ("falling edge detected on machine1")
                        pinvalue=m1.pulseTime()
                       # finalmessage=pinvalue+now+mac+str(pinvalue)
                        fields={'g':pinvalue,'ts':now, 'mac': mac,'pin':MACHINE_CYCLE2 }
                        encoded_args = urllib.urlencode(fields)
                        url = 'http://52.170.42.16:5555/get?' + encoded_args
                        try:
                                r = http.request('GET', url)
                                print('HTTP Send Status: ',r.status)
                        except:
                                print('connection error: ')

def get_mac():
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
        return mac

mac=str(get_mac())


GPIO.add_event_detect(MACHINE_CYCLE, GPIO.BOTH, callback=plcMachine1)
GPIO.add_event_detect(MACHINE_CYCLE2, GPIO.BOTH, callback=plcMachine2)
m1 = Machine(0, 0, 0, 0)
m2 = Machine(0, 0, 0, 0)
print ("Total machines  %d" % Machine.machineCount)

try:
        while True:
                time.sleep(10)
                print("--")
except KeyboardInterrupt:
        print("Quit")
        GPIO.cleanup()
