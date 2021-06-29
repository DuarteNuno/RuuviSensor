import os
import math

from config import *
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from influxdb import InfluxDBClient
import datetime as dt

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

    array=[]

    for new_data in RuuviTagSensor._get_ruuvitag_datas([],10):
        if not contains(new_data,array):
            array.append(new_data)        

    #number of ruuvi read
    print(len(array))

    avg_t=0
    avg_h=0
    avg_p=0
        
    now = dt.datetime.now()

    if len(array)==0: 
        print("unable to connect")

    for i in array:
        json_data=[
                {
                    "measurement": "Data",
                    "fields":
                    {   
                        "Mac_Address": i[0],
                        "Temperature": i[1]["temperature"],
                        "Humidity": i[1]["humidity"],
                        "Air_Pressure": i[1]["pressure"],
                        "Battery": i[1]["battery"],
                        "Movement_Counter": i[1]["movement_counter"]
                    }
            }
        ]

        avg_t += i[1]["temperature"]
        avg_h += i[1]["humidity"]
        avg_p += i[1]["pressure"]

        client.write_points(json_data)
        
    avg_t = avg_t/len(array)
    avg_h = avg_h/len(array)
    avg_p = avg_p/len(array)


    deviation_t = 0
    deviation_h = 0
    deviation_p = 0

    for i in array:
        deviation_t += math.pow(i[1]["temperature"] - avg_t,2)
        deviation_h += math.pow(i[1]["humidity"]    - avg_h,2)
        deviation_p += math.pow(i[1]["pressure"]    - avg_p,2)
        
    json_deviation=[
        {
            "measurement": "Deviation",
            "fields":
            {
                "Deviation_Temperature":math.sqrt(deviation_t/(len(array)-1)),
                "Deviation_Humidity":   math.sqrt(deviation_h/(len(array)-1)),
                "Deviation_Pressure":   math.sqrt(deviation_p/(len(array)-1)),
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

#sudo service grafana-server restart