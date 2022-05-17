import json
import os
import datetime
import serial

def getJSON(filePathAndName):
    with open(filePathAndName, 'r') as fp:
        return json.load(fp)

 
myInfo="" # The JSON Object
lp="" # License Plate
lpC="" # License Plate Confidence 
state =""
time="" # Time Stamp

#If the JSON file is not empty nor saying error than it is good to be Parsed
try:
    empty = os.stat("/home/pi/Desktop/final_project/LPdata.json").st_size == 0

    if not (empty): 
        myInfo=getJSON("/home/pi/Desktop/final_project/LPdata.json")
        if 'error' not in myInfo:
            lp = myInfo['results'][0]['plate'].upper()
            lpC=myInfo['results'][0]['candidates'][0]['score']              
            time=myInfo['timestamp']
                       
               # Data to be written 
            parsedData ={ 
                "LicensePlate":lp,
                "LicensePlateConf":lpC,
                "state":1,
                "TimeStamp":time,   
            } 

            parsedData_blank ={ 
                "LicensePlate":"",
                "LicensePlateConf": "",
                "state":0,
                "TimeStamp":"",   
            } 

            if (lpC > 0.5):
                json_object = json.dumps(parsedData, indent = 4) 
                with open("/home/pi/Desktop/final_project/SendData.json", "w") as outfile: #Write the parsed json in SendData.json on Desktop 
                    outfile.write(json_object)
                # bluetoothSerial.write(b'2')
                print(json_object)
            else:
                json_object = json.dumps(parsedData_blank, indent = 4) 
                with open("/home/pi/Desktop/final_project/SendData.json", "w") as outfile: #Write the parsed json in SendData.json on Desktop 
                    outfile.write(json_object)

    else:
        print("File empty")
#If the JSON file does not respect the specific format than inform me that is not a car
except:
    parsedData_blank ={ 
                "LicensePlate":"",
                "LicensePlateConf": "",
                "state":0,
                "TimeStamp":"",   
            } 
    json_object = json.dumps(parsedData_blank, indent = 4) 
    with open("/home/pi/Desktop/final_project/SendData.json", "w") as outfile: #Write the parsed json in SendData.json on Desktop 
        outfile.write(json_object)
    print("Not a car")