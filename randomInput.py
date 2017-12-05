from random import randint
#print(randint(1, 3))
import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
MACHINE1_CYCLE = 17
MACHINE2_CYCLE = 6
MACHINE1_GOODBAD = 22
MACHINE2_GOODBAD = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(MACHINE1_CYCLE,GPIO.OUT)
GPIO.setup(MACHINE2_CYCLE,GPIO.OUT)
GPIO.setup(MACHINE1_GOODBAD,GPIO.OUT)
GPIO.setup(MACHINE2_GOODBAD,GPIO.OUT)
while True:
        i=randint(1,3)
        good1=randint(0,1)
        good2=randint(0,1)
        #print "goodbad for mchine 1 :",good1
        #print "goodbad for mchine 2 :",good2
        if i==1:
         #       print "genrating test 1 pulse"
                GPIO.output(MACHINE1_GOODBAD,good1)
                GPIO.output(MACHINE2_GOODBAD,good2)
                GPIO.output(MACHINE1_CYCLE,GPIO.LOW)
                GPIO.output(MACHINE2_CYCLE,GPIO.LOW)
                time.sleep(3) # sleep for 3 second
                GPIO.output(MACHINE1_CYCLE,GPIO.HIGH)# Turn on either 0/1 good bad for machine 1
                GPIO.output(MACHINE2_CYCLE,GPIO.HIGH)# Turn on either 0/1 good bad for machine 2
                time.sleep(1)
                GPIO.output(MACHINE1_GOODBAD,GPIO.HIGH)# Turn off good bad for machine 1
                GPIO.output(MACHINE2_GOODBAD,GPIO.HIGH)# Turn off good bad for machine 2
        if i==2:
          #      print "genrating test 2 pulse"
                GPIO.output(MACHINE1_GOODBAD,good1) # Turn on either 0/1 good bad for machine 1
                GPIO.output(MACHINE2_GOODBAD,good2) # Turn on either 0/1 good bad for machine 2
                GPIO.output(MACHINE1_CYCLE,GPIO.LOW)
                time.sleep(1) # sleep for 1 second
                GPIO.output(MACHINE2_CYCLE,GPIO.LOW)
                time.sleep(2) # sleep for 2 second
                GPIO.output(MACHINE1_CYCLE,GPIO.HIGH)
                time.sleep(1) # sleep for 1 second
                GPIO.output(MACHINE1_GOODBAD,GPIO.HIGH) # Turn off good bad for machine 1
                GPIO.output(MACHINE2_CYCLE,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(MACHINE2_GOODBAD,GPIO.HIGH) # Turn off good bad for machine 2
        if i==3 :
           #     print "genrating test 3 pulse"
                GPIO.output(MACHINE1_GOODBAD,good1) #Turn on either 0/1 good bad for machine 1
                time.sleep(1)
                GPIO.output(MACHINE1_CYCLE,GPIO.LOW)
                time.sleep(3) # sleep for 3 second
                GPIO.output(MACHINE1_CYCLE,GPIO.HIGH)#Turn off good bad for machine 1
                time.sleep(1)
                GPIO.output(MACHINE1_GOODBAD,GPIO.HIGH)
                GPIO.output(MACHINE2_GOODBAD,good2)
                time.sleep(2) # sleep for 2 second
                GPIO.output(MACHINE2_CYCLE,GPIO.LOW)
                time.sleep(3) # sleep for 3 second
                GPIO.output(MACHINE2_CYCLE,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(MACHINE2_GOODBAD,GPIO.HIGH)
        time.sleep(1)
        #print "waiting a minute before starting new iteration"
        time.sleep(60)
