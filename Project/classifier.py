from numpy.lib.function_base import average
from classification import Classification
import numpy as np

def classifyStaticVideo(frameData):
    classifications = {}
    prevPanTemp = None

    for frame in frameData:
        timeElapsed, panTemp, panArea, numFood, foodTemp, foodArea = frame

        # Open element or empty pan
        if numFood == 0:

            # Initialize prevPanTemp to be the panTemp of the first sample
            if prevPanTemp is None: prevPanTemp = panTemp
            
            # Determine if the open element or empty pan is heating up or cooling down
            if panTemp >= prevPanTemp:
                classifications[timeElapsed] = Classification.HEATING_UP.name
            else:
                classifications[timeElapsed] = Classification.COOLING_DOWN.name

        # Food is present; Determine if the food is being fried, boiled, or braised
        else:
            # Convert string of food temps to a list of floats
            foodTempList = foodTemp[1:len(foodTemp)-1].split(',')
            foodTempList = [float(foodTempElement.strip()) for foodTempElement in foodTempList]

            # Classify cooking method based on temperature difference between pan and food
            if panTemp > 200 or any(foodTempList) > panTemp or average(foodTempList) < panTemp - 50:
                classifications[timeElapsed] = Classification.FRYING.name

            # Boiling water doesn't seem to go over 140 degrees
            elif panTemp - 50 <= average(foodTempList) < panTemp:
                classifications[timeElapsed] = Classification.BOILING.name

            else:
                classifications[timeElapsed] = Classification.UNKNOWN.name

        # Store pan temp so we can detect if the pan is heating up or cooling down
        prevPanTemp = panTemp

    return classifications