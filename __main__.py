import os
import math

from config import *
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from influxdb import InfluxDBClient

#start influxdb
def config_influxdb():
    client=InfluxDBClient (host=HOST,port=PORT)
    client.switch_database(DB)
    
    return client

#check if file is part of array
def contains(file,array):
    if array==[]:
        return False
    
    for header in array:
        if header[0]==file[0]:
            return True
    
    return False

#get Data from ruuvi and store in influxdb
def collect_influxdb(client = InfluxDBClient() ):
    os.environ['RUUVI_BLE_ADAPTER'] = "Bleson"

    #array of sensors
    sensors=[]

    for new_data in RuuviTagSensor._get_ruuvitag_datas([],10):
        if not contains(new_data,sensors):
            sensors.append(new_data)        

    #number of ruuvi read
    print(len(sensors))

    avg_t=0
    avg_h=0
    avg_p=0
        
    if len(sensors)==0: 
        print("unable to connect")

    for tag in sensors:
        json_data=[
                {
                    "measurement": "Data",
                    "fields":
                    {   
                        "Mac_Address": tag[0],
                        "Temperature": tag[1]["temperature"],
                        "Humidity": tag[1]["humidity"],
                        "Air_Pressure": tag[1]["pressure"],
                        "Battery": tag[1]["battery"],
                        "Movement_Counter": tag[1]["movement_counter"]
                    }
            }
        ]

        avg_t += tag[1]["temperature"]
        avg_h += tag[1]["humidity"]
        avg_p += tag[1]["pressure"]

        client.write_points(json_data)
        
    avg_t = avg_t/len(sensors)
    avg_h = avg_h/len(sensors)
    avg_p = avg_p/len(sensors)


    deviation_t = 0
    deviation_h = 0
    deviation_p = 0

    for tag in sensors:
        deviation_t += math.pow(tag[1]["temperature"] - avg_t,2)
        deviation_h += math.pow(tag[1]["humidity"]    - avg_h,2)
        deviation_p += math.pow(tag[1]["pressure"]    - avg_p,2)
        
    json_deviation=[
        {
            "measurement": "Deviation",
            "fields":
            {
                "Deviation_Temperature":math.sqrt(deviation_t/(len(sensors)-1)),
                "Deviation_Humidity":   math.sqrt(deviation_h/(len(sensors)-1)),
                "Deviation_Pressure":   math.sqrt(deviation_p/(len(sensors)-1)),
            }
        }
    ]

    client.write_points(json_deviation)

    #database updated
    print("SAVED")

    os.environ.pop('RUUVI_BLE_ADAPTER')

if __name__ == '__main__' :
    client = config_influxdb()
    while(True):
        collect_influxdb(client)
        