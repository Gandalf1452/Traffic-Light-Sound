
# test BLE Scanning software
# team WDF v2x group updated 5/5/17
# Mr. I updates - 8/3/17
#
import blescan
import sys
import bluetooth._bluetooth as bluez
from squid import*
import time
import os

whichPi = "iHop"
status = "normal"
# options are normal and emergency


dev_id = 0
try:
        sock = bluez.hci_open_dev(dev_id)
        print "ble thread started"

except:
        print "error accessing bluetooth device..."
        sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)


rgb1 = Squid(18,23,24) # Declare pins to use for first RGB squid -- global use
rgb2 = Squid(16,20,21) # Declare pins to use for the second RGB squid
rgbstatus1 = "None"
rgb2status = "None"


# Create a list of the Beacon IDs we "care" about...
knownDevices = ["0c:f3:ee:00:68:e8","0c:f3:ee:0d:7d:71"]

# GOAL IDEA... #if (beacon id) == (seenDevices) then (do the right thing for that device ... ambulance, traffic light, etc)


def normalTraffic():

        global status
        global rgbstatus1, rgb2status

        while True:
                beaconScan()
                print status + " status:  Top of normal function"
                if (status  == "emergency"):
                        emergencyTraffic()
                else:
#                       rgb1.set_color(RED)
#                       rgbstatus1 = "RED"
                        rgb2.set_color(RED)
                        rgb2status = "RED"
                        time.sleep(1)
                        #Set both lights to RED

                        rgb1.set_color(GREEN)
                        rgbstatus1 = "GREEN"
                        time.sleep(8)
                        rgb1.set_color((75,5,0))
                        rgbstatus1 = "YELLOW"
                        time.sleep(2)
                        rgb1.set_color(RED)
                        rgbstatus1 = "RED"
                        time.sleep(1)

                        rgb2.set_color(GREEN)
                        rgb2status = "GREEN"
                        time.sleep(8)
                        rgb2.set_color((75,5,0))
                        rgb2status = "YELLOW"
                        time.sleep(2)

                        print "Reset normal"
                        print rgbstatus1, rgb2status
        GPIO.cleanup()

def emergencyTraffic():

        global rgbstatus1, rgb2status

        print "Emergency Vehicle Detected: Adjust Lights"

        if (rgbstatus1 == "GREEN"):
                rgb1.set_color((75,5,0))
                time.sleep(2)
                rgb1.set_color(RED)
                time.sleep(5)
        elif (rgbstatus1 == "YELLOW"):
                rgb1.set_color(RED)
                time.sleep(5)
        elif (rgbstatus1 == "RED"):
                rgb1.set_color(RED)
                time.sleep(5)
        if (rgb2status == "GREEN"):
                rgb2.set_color((75,5,0))
                time.sleep(2)
                rgb2.set_color(RED)
                time.sleep(5)
        elif (rgb2status == "YELLOW"):
                rgb2.set_color(RED)
                time.sleep(5)
        elif (rgb2status == "RED"):
                rgb2.set_color(RED)
                time.sleep(5)
#       else:
#               normalTraffic()

        rgbstatus1 = "RED"
        rgb2status = "RED"
	os.system("omxplayer /home/pi/ambulance_new.wav")

def beaconScan():
        global status

        print "Scanning for BLEs"
#       while True:
        returnedList = blescan.parse_events(sock, 7)
        print returnedList
        print "   <=============="

        print "----------"
        numValues = len(returnedList) # Not useful!  Always the 2nd param in the beacon scan
        print "There were {} devices detected *-*-*-*-*-".format(numValues)

        if numValues>0 :
                print "Devices found"
                print " ==> Analyzing Data <=="

                listBeacons=[]  # Refresh beacon list -- empty previous items --

#       print "out of normal"

                for beacon in returnedList:
                #print (beacon[0:17])
                        listBeacons.append(beacon[0:17])
                        uniqueList=set(listBeacons)
#               ^this turns all of our ble signals into the list and keeps them from repeating
        # AFTER the loop is done, print JUST the unique IDs of the beacons found during the scan
                print "Unique Beacons found: ".format(uniqueList)
                print "----------"
#               print "************"
#               print "Wanted devices..."
#       matchedDevices = list(set(uniqueList & set(knownDevices))


        # intersection will identify OVERLAP in two sets -- think Venn Diagram...
                matchedDevices = set.intersection(uniqueList,knownDevices)

                if len(matchedDevices)<1:
                        print "No emergency vehicles detected"
                        status="normal"
                else:
                        emvsDetected = 0
                        nonEMVsDetected = 0
                        #Reset beacons/vehicles detected back to ZERO
                        print "Testing {} devices - loop repeats for EMVs".format(len(matchedDevices))
                        for beaconSeen in matchedDevices:
                                if (whichPi == "iHop") and (beaconSeen == "0c:f3:ee:00:68:e8"):
                                        print "Smart Traffic Light detected Emergency Vehicle"
                                        status="emergency"
                                        print status + ": Bottom of beacon scan ELSE "
                                        emvsDetected = emvsDetected +1

                                else:
                                        nonEMVsDetected = nonEMVsDetected+1
                                        print "THIS Beacon: {} : not connected to emergency vehicle".format(beaconSeen)
                                        if (emvsDetected <1) and (nonEMVsDetected == len(matchedDevices)):
                                                status="normal"

#                               emergencyTraffic()
#                       else: status = "normal"
#               normalTraffic()
#       print status + ": Bottom of Scan Loop"

        else:
                print "NO BEACONS DETECTED THIS TIME AROUND"
        print "*** End of Scan Loop *********"
        #Maybe stick a for loop down here, say for knownDevices[1] in matchedDevices:
                                                        #--- maybe import code? ---
                                                        #--- or maybe do a Read File from traffic light code ---
normalTraffic()
