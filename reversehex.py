import sys
import math
import struct

def floatToReversedChar(floatvalue):
    radiansint=int(math.radians(floatvalue)*10000000)
    char1 = (radiansint>>24) & 0xff
    char2 = (radiansint>>16) & 0xff
    char3 = (radiansint>>8) & 0xff
    char4 = radiansint & 0xff
    array=[char4,char3,char2,char1]
    return array
	
#-----------------------------------try to encode longitude
longitude=113.952271
latitude=22.53701
print('Longitude: '+str(longitude))

#print(hex(char4)+hex(char3)+hex(char2)+hex(char1))
array=floatToReversedChar(longitude)
print(hex(array[0])+hex(array[1])+hex(array[2])+hex(array[3]))

#0x12f7927   #\x30\x79\x2f\x01

#-----------------------------------try to encode longitude