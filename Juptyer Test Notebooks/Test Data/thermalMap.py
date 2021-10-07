import cv2
import numpy as np
import math
from colormap import rgb2hex

class ThermalMap:
    def __init__(self):
        self.tempRange = np.load('fixedTempScale.npy')
        self.rgbScaleInt = np.load('fixedRgbIntScale.npy')
        self.high = 350
        self.low = -50


    def rgb2int(self, rgb):
        hex = rgb2hex(rgb[0], rgb[1], rgb[2])
        return int(hex[1:len(hex)], 16)

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return (array[idx], idx)

    def get_temp(self, val):
        temp, idx = self.find_nearest(self.rgbScaleInt, val)
        return self.tempRange[idx]

    def rgb_to_temp(self, image):
        img = cv2.imread(image, cv2.COLOR_BGR2RGB)

        rgbArr = np.array(img)

        x = rgbArr.shape[0] #Rows
        y = rgbArr.shape[1] #Cols

        tempMapped = np.empty([x, y])

        for row in range(0, x):
            for col in range(0, y):
                tempMapped[row,col] = self.get_temp(rgb2int(rgbArr[row,col]))

        return tempMapped  

    def newTempRange(self, img, high, low):
        self.low = low
        self.high = high

        tempScaleImg = cv2.imread(img)
        tempArr = np.array(tempScaleImg)
        
        x = tempArr.shape[0] #Rows
        y = tempArr.shape[1] #Cols
        

        #Find the average rgb value in each row
        tempAvgArr = tempArr[0:x, 0]
        self.rgbScaleInt = np.empty([x])
        for i in range(0, x):
            self.rgbScaleInt[i] = self.rgb2int(tempAvgArr[i])

        self.tempRange = np.linspace(high, low, x)


    def defaultRange(self):
        self.tempRange = np.load('fixedTempScale.npy')
        self.rgbScaleInt = np.load('fixedRgbIntScale.npy')


