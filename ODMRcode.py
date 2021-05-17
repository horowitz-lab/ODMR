"""
Created on Saturday Feb 27 2021

@authors: Lucas Wright
for help pyvisa documentaion:
https://pyvisa.readthedocs.io/en/latest/introduction/example.html
"""

#--------------------------------Library Imports------------------------------#


import pyvisa
from datetime import date
import time
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import winsound


#make the GPIB global
rm = pyvisa.ResourceManager()
instList = rm.list_resources()
#connecting to the instroments:
photonCounter = rm.open_resource('GPIB0::23::INSTR')
micEmit = rm.open_resource('GPIB0::27::INSTR')




#--------------------------Setting Up GPIB Connectivity-----------------------#
"""fxn to return the GBIP objects (DONE)"""
def findGPIBs ():
    #get in contact with the PhotonCounter and MicEmit
    rm = pyvisa.ResourceManager()
    instList = rm.list_resources()
    print(instList)
    #connecting to the instroments:
    photonCounter = rm.open_resource('GPIB0::23::INSTR')
    micEmit = rm.open_resource('GPIB0::27::INSTR')
    return (photonCounter, micEmit)



   
"""This fxn will call measure() many times to build the data list (DONE)"""
def collectData(freq_width, centered_freq, num_of_readings, legnth_of_collection, amplitude):
   
    #set the amp of the MicEmit
    AmpStr = "AMPR"+str(amplitude)
    micEmit.write(AmpStr)
    centered_freq = centered_freq-200
    #generate the list of data point we want to get pointlist[[freqLocation, length of collection],[]...]:
    stepSize = freq_width/num_of_readings
    starting_freq = (centered_freq - freq_width/2)
    pointList = []
   
    for j in range(num_of_readings):
        pointList.append([starting_freq + (stepSize * j), legnth_of_collection])
   
    #shuffle this list to decrease systematic error
    random.shuffle(pointList)
   
    #create an empty list to store the data:
    dataList = []
    #run a loop to gather the points:
    for freq in pointList:
        dataList.append(measure(freq[0], freq[1]))

    #here we convert to an array for funcationality
   
    dataListArray = np.array(dataList)
   
    # here we send the list on the form dataList = [[freq, count]...]
    return (dataListArray)




""" this is where the actual measurement of the data will happen.
Still need to figure out how to capture the photon counts for a given time"""
def measure(freq, legnth_of_collection):
   
    #set the microwave to correct freq\
    micEmit.query("FREQ?")
    freqStr = "FREQ"+str(freq)
    micEmit.write(freqStr)
   
    #sleep for a set to let micEmit start making the signal
    time.sleep(.2)
   
    # count start
    photonCounter.write("cs")
    #important, needs time to start the count must be larger than 1 sec!!!
    time.sleep(1)
       
    #ask SR400 to give the photon count
    count = int(photonCounter.query("QA"))
    print(count)
    photonCounter.write("cr")
    return([freq, count])
       



""" takes data as an array of points [[freq,count]...] plots changes in count
normalized by the lowest value"""
def plotValues(dataList):
   
    #(BASIC) here we are plotting the two coloums against eachother
    plt.scatter(dataList[:,0], dataList[:,1])
    plt.show()




def saveFile(data, name = (str(time.clock) + str(date.fromisoformat('2019-12-04')))):
    my_df = {'freq': data[:,0],
             'photon count': data[:,1]}
   
   
    pd.DataFrame(my_df).to_csv("C:/Users/HorowitzLab/Desktop/Lucas MicWave data/bigersweep.csv", index = False)
   
 
   
   
def main():
    #User input Vars:
        #Hz
    freq_width = 0.03e9
        #Hz range 950kHz-6.075GHz
    centered_freq = 2.873e9
    #this is the number of readings we will take
    num_of_readings = 1000
        #sec
    legnth_of_collection = 0.5
        #dBm range(-110-16.5)
    Amplitude = 16.5
    micEmit.write("AMPR 16.5")
   
    # def collectData(freq_width, centered_freq, num_of_readings, legnth_of_collection):
    dataList = collectData(freq_width, centered_freq, num_of_readings, legnth_of_collection, Amplitude)
    #take data and your file name, will save to desktop folder Lucas micWave data dataList(ARRAY)
    saveFile(dataList, "test")
    duration = 1000  # milliseconds
    freq = 440  # Hz
    winsound.Beep(freq, duration)
   
    plotValues(dataList)
   
   
   
   
if __name__=='__main__':
    main()


