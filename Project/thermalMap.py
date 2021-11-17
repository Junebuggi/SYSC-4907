import cv2
import numpy as np
import math
from colormap import rgb2hex

class ThermalMap:
    def __init__(self):
        self.tempRange = np.load('Project/fixedTempScale.npy')
        self.rgbScaleInt = np.load('Project/fixedRgbIntScale.npy')
        self.rgbScale = np.load('Project/fixedRgbScale.npy')
        self.high = 350
        self.low = -50


    def rgb2int(self, rgb):
        hex = rgb2hex(rgb[0], rgb[1], rgb[2])
        return int(hex[1:len(hex)], 16)

    def closest(self, arr, color):
        colors = arr
        color = np.array(color)
        distances = np.sqrt(np.sum((colors-color)**2,axis=1))
        index_of_smallest = np.where(distances==np.amin(distances))
        smallest_distance = colors[index_of_smallest]
        return smallest_distance, index_of_smallest

    def get_temp(self, val):
        temp, idx = self.closest(self.rgbScale, val)
        return self.tempRange[idx][0]

    def rgb_to_temp(self, image):
        img = cv2.imread(image, cv2.COLOR_BGR2RGB)

        rgbArr = np.array(img)

        x = rgbArr.shape[0] #Rows
        y = rgbArr.shape[1] #Cols

        tempMapped = np.empty([x, y])

        for row in range(0, x):
            for col in range(0, y):
                tempMapped[row,col] = self.get_temp(rgbArr[row,col])

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
        self.tempRange = np.load('Project/fixedTempScale.npy')
        self.rgbScaleInt = np.load('Project/fixedRgbIntScale.npy')


