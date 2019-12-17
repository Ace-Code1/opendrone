import sys
import math
import struct

def floatToReversedIntArray(floatvalue):
    radiansint=int(math.radians(floatvalue)*10000000)
    char1 = (radiansint>>24) & 0xff
    char2 = (radiansint>>16) & 0xff
    char3 = (radiansint>>8) & 0xff
    char4 = radiansint & 0xff
    array=[char4,char3,char2,char1]
    return array

def hexArrayToFloat(hexArray):
    floatValue=0
    floatValue=int(hexArray[3])<<24
    floatValue+=(int(hexArray[2])<<16)
    floatValue+=(int(hexArray[1])<<8)	
    floatValue+=int(hexArray[0])
    floatValue=math.degrees(float(floatValue)/10000000)
    return floatValue



	
#-----------------------------------try to encode longitude
longitude=113.952271
latitude=22.54701
print('Coordinate: '+str(latitude))

array=floatToReversedIntArray(latitude)
print(hex(array[0])+hex(array[1])+hex(array[2])+hex(array[3]))
floatagain=hexArrayToFloat(array)
print(floatagain)

#-----------------------------------try to encode longitude
