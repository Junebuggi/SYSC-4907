import cv2
import numpy as np
import math
import sys
from colormap import rgb2hex
from matplotlib import pyplot as plt
import time
import thermalMap as ThermalMap
import math
import random as rng
from operator import itemgetter

thermalObj = ThermalMap.ThermalMap()

def sampleVideo(vid, sampleRate):
    
    video = cv2.VideoCapture(vid)

    fps = video.get(cv2.CAP_PROP_FPS)
    #Therefore we need to sample every xth frame
    sampleDuration = fps * sampleRate
    sampledList = []
    index = 0
    ret, frame = video.read()
    sampledList.append(frame)
    while(True):
        ret, frame = video.read()
        if not ret: 
            break
        if index%(sampleDuration)==0:
            sampledList.append(frame)
        index += 1
    
    return sampledList

def resizeImage(img, percent):
    width = int(img.shape[1] * percent / 100)
    height = int(img.shape[0] * percent / 100)
    dim = (width, height)

    # resize image
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

def cropImage(img, percent):
    width = img.shape[1]
    height = img.shape[0]
    widthCrop = int(width * percent / 100)
    heightCrop = int(height * percent / 100)
    return img[heightCrop:height-heightCrop, widthCrop:width-widthCrop]

def getContourHeat(contours, img, frame):
    # For each list of contour points...
    contourFeatures = []
    for i in range(len(contours)):
        # Create a mask image that contains the contour filled in
        cimg = np.zeros_like(img)
        
        cv2.drawContours(cimg, contours, i, color=255, thickness=-1)

        # Access the image pixels and create a 1D numpy array
        pts = np.column_stack(np.where(cimg == 255))
        totalTemp = 0
        for i in range(len(pts)):
            r = int(frame[pts[i][0], pts[i][1]][0])
            g = int(frame[pts[i][0], pts[i][1]][1])
            b = int(frame[pts[i][0], pts[i][1]][2])
            rgb = (r, g, b)
            temp = thermalObj.get_temp(rgb)
            totalTemp += temp
        avgTemp = totalTemp/(len(pts))
        #print("Average Temp of Contour is: %.2f" % avgTemp, "°C")
        contourFeatures.append((avgTemp, len(pts)))
    return contourFeatures

def getAverageImageTemperature(image):
    height, width, channels = image.shape
    sum = 0
    for x in range(0, width-1):
        for y in range(0, height-1):
            rgb = (int(image[y,x][0]), int(image[y,x][1]), int(image[y,x][2]))
            temp = thermalObj.get_temp(rgb)
            sum += temp

    return sum / (height*width)

def contourMask(image):
    pts = np.where(image != 0)
    #print(len(pts[0]))
    coordinates = []
    for i in range(len(pts[0])):
        coordinates.append((pts[0][i], pts[1][i]))
    return coordinates

def getPercentageOfMode(image):
    height, width, channels = image.shape
    sum = 0
    temps = []
    for x in range(0, width-1):
        for y in range(0, height-1):
            rgb = (int(image[y,x][0]), int(image[y,x][1]), int(image[y,x][2]))
            temps.append(thermalObj.get_temp(rgb))

    counts, bins = np.histogram(temps, 15)
    sum = np.sum(counts)
    return (np.amax(counts)/sum)

def thresh_callback(frame, image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
    
    # Find the rotated rectangles and ellipses for each contour
    if biggest_contour.shape[0] > 5:
            minEllipse = cv2.fitEllipse(biggest_contour)

    # Draw contours + rotated rects + ellipses
    contours = [biggest_contour]
    blackFrame = 0 * np.ones((image.shape[0], image.shape[1],3), np.uint8)
    for i, c in enumerate(contours):
        color = (255, 255, 255) #White
        # ellipse
        if c.shape[0] > 5:
            cv2.ellipse(blackFrame, minEllipse, color, -1)
    return blackFrame

def getAverageTemperature_pnts(pnts, image):
    sum = 0
    for x in pnts:
        rgb = (int(image[x][0]), int(image[x][1]), int(image[x][2]))
        sum += int(thermalObj.get_temp(rgb))

    return sum/len(pnts)

def removeNoise(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray,9,75,75)
    return blur

def getContoursInsidePan(image, frame):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
    image_cpy = frame.copy()
    cv2.drawContours(image=image_cpy, contours=contours, contourIdx=-1, color=(0,255,255),
                thickness=1, lineType=cv2.LINE_AA)
    
    return image_cpy, contours

def thermalImagingProcess_toTable(frames):
    #Iterate over every sampled frame in video
    backgroundTemp = 24
    background = resizeImage(frames[0], 25)
    prevIsBG = True
    entries = []
    i=0
    for frame in frames:
        #Resize and crop image to improve image processing speed
        frame = resizeImage(frame, 25)
        #showImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), "Original")
        #If over 85% of the image has same colour, then it is considered 
        if prevIsBG and getPercentageOfMode(frame) >= 0.90:
            background = frame.copy()
            backgroundTemp = getAverageImageTemperature(frame)
        else:
            prevIsBG = False
            foreground = frame.copy()

            foreground = removeNoise(foreground)
            thresh = cv2.adaptiveThreshold(foreground, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
            ellipse = thresh_callback(frame, thresh)

            ellipseMask = cv2.bitwise_and(frame, ellipse)
            if len(np.column_stack(np.where(ellipse != 0))) == 0:
                backgroundTemp = getAverageImageTemperature(frame)
                background = frame.copy()
            else:
                #showImage(cv2.cvtColor(ellipseMask, cv2.COLOR_BGR2RGB), "Ellipse")
                pnts = list(set(contourMask(ellipse)))
                panTemp = getAverageTemperature_pnts(pnts, frame)
                if backgroundTemp - panTemp > - 10:
                    backgroundTemp = getAverageImageTemperature(frame)
                    background = frame.copy()
                else:
                    foreground = removeNoise(ellipseMask)
                    thresh = cv2.adaptiveThreshold(foreground, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
                    insidePan, contours = getContoursInsidePan(cv2.cvtColor(cv2.bitwise_and(cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR), ellipse), cv2.COLOR_RGB2GRAY), frame)
                    #getTemperatureHist_pnts(ellipseMask, pnts)
                    pts = getContourHeat(contours, thresh, frame)
                    pts = list(filter(lambda x: x[1] > 50, pts))
                    pan = max(pts,key=lambda item:item[1])
                    if(len(pts) > 1):
                        food = pts.copy()
                        food.remove(pan)
                        #Now remove food from pan pixels and average temp
                        for f in food:
                            panAvg = (pan[0]*pan[1]-f[0]*f[1])/(pan[1]-f[1])
                            pan = (panAvg, pan[1] - f[1])
                        foodTemp = [x[0] for x in food]
                        foodSize = [x[1] for x in food]
                        entries.append([i*10, pan[0], pan[1], len(food), str(foodTemp),str(foodSize)])
                    else:
                        entries.append([i*10, pan[0], pan[1], len(food), "", ""])
        i += 1
    return entries
                    
"""
This function will sample a thermal video with a rate of sampleRate
and will add the data derived for each frame to the table
"""
def processVideo(video, sampleRate):
    frames = sampleVideo(video, sampleRate)
    entries = thermalImagingProcess_toTable(frames)
    return entries

