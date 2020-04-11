#beacons = {'SR1': ('U', 'LS', 'RS'), 'SR2': ('S', 'SD'), "FARADAY" : ('S', 'SD')}

# SR1->T SR2 FARADAY
# SR2->FARADAY  or SR2->down
# Faraday->sr2 or faraday->down

#directionaldict = {'S': 'straight', 'D': 'down', 'U': 'up', 'LS': 'left turn walk straight', 
#'RS': 'right turn walk straight', 'SD': 'straight down'}

listReadings = [("Beacon1", 10), ("Beacon2", 30), ("Beacon3", 50)]
listRSSI = []
for item in listReadings:
    listRSSI.append(item[1])

def maxRSSI(_listRSSI):
    return getMax(listRSSI)
# Use max RSSI val and find corresponding beacon
# need required get functions
# Use maxRSSi and find corresponding beacon name
beaconval = 5
curBeacon = "SR1"
endBeacon = "FARADAY"
switch = True
while(switch):

    #curBeaacon = getUpdatedBeacon()
    if (curBeacon == 'SR1' and endBeacon == 'FARADAY'):
        print("go up " + " turn left and walk straight")
    if (curBeacon == 'SR1' and endBeacon == 'SR2'):
        print("go up " + " turn left and walk straight")
    if (curBeacon == 'SR2' and endBeacon =='SR1'):
        print("walk straight and take first left" + " go down")
    if (curBeacon == 'SR2' and endBeacon == 'FARADAY'):
        print("walk straight all the way")
    if (curBeacon == 'FARADAY' and endBeacon == 'SR2'):
        print("walk straight all the way")
    if (curBeacon == 'FARADAY' and endBeacon == 'SR1'):
        print("walk straight and take first right "+ "go down")
    if (curBeacon == endBeacon):
        print("destination reached")
        break

#@ represents a beacon, X represents a spot without a beacon, O represents person, T represents target

'''
# intialize all pts to be Xs
map = [['X' for length in range(LENGTH)] for floor in range(FLOOR)]

print(map)
#print(map[0][1])
# if 2 beacons intialize at the ends of each floor
'''
'''editMarker(map, 1, 9, )

print(map)
# requires get input from other files

first_marker = True
saveScale = 0

# first inital entry
if first_marker == True:
    temp = scaleRSSI(-50, 30)
    editMarker(map, 1, temp, 0, 'O')
    saveScale = temp
    first_marker = False
#subsequent entries which are false after first entry
else:
    editMarker(map, 1, saveScale, 0, 'X')
    temp = scaleRSSI(-50, 30)
    editMarker(map, 1, temp, 0, 'O')
    saveScale = temp
'''

#def editMarker(map, _floor, _length, marker):

#    if (map[_floor][_length] == '@'):
    
#    else:
#        map[_floor][_length] = 'X'

#def scaleRSSI(_rssi1, _rssi2):
#    total = abs(_rssi1) + abs(_rssi2)
#    if _rssi1 > _rssi2:
#        scaled_val = round(abs((_rssi1)/total)*LENGTH)
#    else:
#        scaled_val = round(abs((total-_rssi2/total)*LENGTH)

#    return scaled_val

#first add target
#editMarker(map, 1, 4, 'T')
#add beacons