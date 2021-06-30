from csv import writer
import os
import time

from ruuvitag_sensor.ruuvi import RuuviTagSensor
import datetime as dt

def contains(file,array):
    if array==[]:
        return False
    for header in array:
        if header[0]==file[0]:
            return True
    
    return False

"""
get Data from ruuvi and save in csv
"""
def collect_csv():
    while(True):
        os.environ['RUUVI_BLE_ADAPTER'] = "Bleson"

        array=[]

        for new_data in RuuviTagSensor._get_ruuvitag_datas([],10):
            if contains(new_data,array):
                continue
            array.append(new_data)

        print(len(array))

            
        now = dt.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")

        f = open("datas_collect.csv", "a")

        if len(array)==0: 
            List = [date,"unavailable"]
            writer_object = writer(f)
            writer_object.writerow(List)
            
        for i in array:
            print('OK')
            List = [date,
                    i[0],
                    i[1]["battery"],
                    i[1]["humidity"],
                    i[1]["temperature"],
                    i[1]["pressure"],
                    i[1]["movement_counter"]
                    ]
            writer_object = writer(f)
            writer_object.writerow(List)

        f.close()
        print("SAVED")

        os.environ.pop('RUUVI_BLE_ADAPTER')
        time.sleep(15*59)

if __name__ == 'collect' :
    collect_csv()