#Start with $ export RUUVI_BLE_ADAPTER="Bleson"

import os
import time
import json
import math

from ruuvitag_sensor.decoder import UrlDecoder, Df3Decoder
from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
from ruuvitag_sensor.ruuvitag import RuuviTag
from influxdb import InfluxDBClient
import datetime as dt

#open db
client=InfluxDBClient (host="localhost",port="8086")
client.switch_database("environmental_monitoring")

def contains(file,array):
    if array==[]:
        return False
    for header in array:
        if header[0]==file[0]:
            return True
    
    return False

#get Data from ruuvi
while(True):
    os.environ['RUUVI_BLE_ADAPTER'] = "Bleson"

    array=[]

    for new_data in RuuviTagSensor._get_ruuvitag_datas([],10):
        if contains(new_data,array):
            continue
        array.append(new_data)

    print(len(array))

    avg_t=0
    avg_h=0
    avg_p=0
        
    now = dt.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    if len(array)==0: 
        print("unable to connect")
        

    for i in array:
        print('OK')

        json_data={
                "measurement": "Data",
                "fields":
                {   
                    #create new filed relative time
                    "Mac_Address": i[0],
                    "Temperature": i[1]["temperature"],
                    "Humidity": i[1]["humidity"],
                    "Air_Pressure": i[1]["pressure"],
                    "Battery": i[1]["battery"],
                    "Movement_Counter": i[1]["movement_counter"]
                }
        }


        avg_t += i[1]["temperature"]
        avg_h += i[1]["humidity"]
        avg_p += i[1]["pressure"]

        client.write_points(json_data)



    json_average=[
        {
            "measurement": "Average",
            "fields":
            {
                "Average_Temperature": avg_t/len(array),
                "Average_Humidity": avg_h/len(array),
                "Average_Air_Pressure": avg_p/len(array),
            }
        }
    ]
    client.write_points(json_average)

    deviation_t = 0
    deviation_h = 0
    deviation_p = 0

    for i in array:
        deviation_t += math.pow(i[1]["temperature"] - (avg_t/len(array)),2)
        deviation_h += math.pow(i[1]["humidity"]    - (avg_h/len(array)),2)
        deviation_p += math.pow(i[1]["pressure"]    - (avg_p/len(array)),2)
        

    json_error=[
        {
            "measurement": "Error",
            "fields":
            {
                "Error_Temperature":math.sqrt(deviation_t/(len(array)-1))/math.sqrt(len(array)),
                "Error_Humidity":   math.sqrt(deviation_h/(len(array)-1))/math.sqrt(len(array)),
                "Error_Pressure":   math.sqrt(deviation_p/(len(array)-1))/math.sqrt(len(array)),
            }
        }
    ]

    client.write_points(json_error)

    print("SAVED")

    os.environ.pop('RUUVI_BLE_ADAPTER')

#sudo service grafana-server restart